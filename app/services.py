import eventlet
import serial

from app.socket_connection import emit_status, emit_lap, emit_cu_status
from app.control_unit_connection import connect
from app import app
from app.models import Race, Timing
from carreralib import connection
from carreralib import ControlUnit


eventlet.monkey_patch()

control_unit_connection_thread = None


def handle_control_unit_events():
    cu = connect()

    current_race = Race.current()
    if current_race is not None and current_race.status == 'created':
        current_race.start
    cu.reset()
    cu.start()

    timings = [Timing(num) for num in range(0, 8)]
    last_status_or_timer = None
    while True:
        app.logger.info("*")
        try:
            app.logger.info("Requesting ControlUnit Data")
            status_or_timer = cu.request()
            app.logger.info("Processing ControlUnit Data")
            if status_or_timer == last_status_or_timer:
                app.logger.info("*--")
                continue
            if isinstance(status_or_timer, ControlUnit.Status):
                app.logger.info("processing a status " + repr(status_or_timer))
                emit_status(status_or_timer)

            elif isinstance(status_or_timer, ControlUnit.Timer):
                app.logger.info("processing a timer " + repr(status_or_timer))
                controller = int(status_or_timer.address)
                timing = timings[controller]
                timing.newlap(status_or_timer)
                if current_race is not None:
                    current_race.add_lap(controller, timing.lap_time)
                emit_lap(status_or_timer, timing)
            app.logger.info("**")
            last_status_or_timer = status_or_timer
            eventlet.sleep(1.0)
        except serial.serialutil.SerialException:
            app.logger.info('got SerialExcpetion')
            emit_cu_status('disconnected', 'unknown')
            cu = connect()
        except connection.TimeoutError:
            app.logger.info('got TimeoutServer')
            emit_cu_status('timeout', 'unknown')
            cu = connect()
        except connection.ConnectionError:
            app.logger.info('got TimeoutServer')
            emit_cu_status('connect_error', 'unknown')
            cu = connect()
        except eventlet.StopServe:
            app.logger.info('received eventlet.StopServe')
            return
    app.logger.info("Out of processing loop, exiting...")


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
