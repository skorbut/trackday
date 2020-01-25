import eventlet
import serial

from app.socket_connection import emit_status, emit_lap, emit_cu_status
from app.control_unit_connection import connect
from app.sleep_calculator import calculate_sleep_time
from app import app
from app.models import Race, Timing
from carreralib import connection
from carreralib import ControlUnit


eventlet.monkey_patch()

control_unit_connection_thread = None


def handle_control_unit_events():
    app.logger.info("* starting handle_control_unit_events")
    current_race = Race.current()
    while True:
        try:
            cu = connect()
            app.logger.info("* got connection to cu")
            app.logger.info("* resetting cu")
            cu.reset()
            app.logger.info("* starting cu")
            cu.start()
            if current_race is not None and current_race.status == 'created':
                current_race.start()
            break
        except connection.TimeoutError:
            app.logger.info('* got TimeoutError during cu.reset / cu.start')
            emit_cu_status('timeout', 'unknown')

    timings = [Timing(num) for num in range(0, 8)]
    last_status_or_timer = None
    last_status = None
    while True:
        if current_race is None:
            current_race = Race.current()
        try:
            status_or_timer = cu.request()
            if status_or_timer == last_status_or_timer:
                continue
            if isinstance(status_or_timer, ControlUnit.Status):
                emit_status(status_or_timer)
                last_status = status_or_timer
            elif isinstance(status_or_timer, ControlUnit.Timer):
                controller = int(status_or_timer.address)
                timing = timings[controller]
                timing.newlap(status_or_timer)
                if current_race is not None:
                    current_race.add_lap(controller, timing.lap_time)
                emit_lap(status_or_timer, timing)
            last_status_or_timer = status_or_timer
            emit_cu_status('connected', 'unknown')
            eventlet.sleep(calculate_sleep_time(current_race, last_status))
        except serial.serialutil.SerialException:
            emit_cu_status('disconnected', 'unknown')
            cu = connect()
        except connection.TimeoutError:
            emit_cu_status('timeout', 'unknown')
            cu = connect()
        except connection.ConnectionError:
            emit_cu_status('connect_error', 'unknown')
            cu = connect()
        except eventlet.StopServe:
            return
    app.logger.info("* Out of processing loop, exiting...")


def try_control_unit_connection():
    global control_unit_connection_thread
    if control_unit_connection_thread is None:
        app.logger.info('Initializing cu listener thread')
        control_unit_connection_thread = eventlet.spawn(handle_control_unit_events)
    else:
        app.logger.info('control_unit_connection thread is already created')


def disconnect_control_unit():
    global control_unit_connection_thread
    if control_unit_connection_thread is not None:
        app.logger.info('disconnecting Control Unit...')
        control_unit_connection_thread.kill()
        control_unit_connection_thread = None
        app.logger.info('control_unit_connection thread killed')
