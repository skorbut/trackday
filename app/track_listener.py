import eventlet
import greenlet
import time

from app import app
from app.sleep_calculator import calculate_sleep_time
from app.control_unit_connection import ControlUnitConnection

from carreralib import ControlUnit

eventlet.monkey_patch()
track_listener_thread = None


def listen(status_observer, time_observer):
    last_status_or_timer = None
    last_status = None
    connection = ControlUnitConnection()
    if not connection.connected():
        return

    app.logger.info("Starting event loop")
    while True:
        try:
            status_or_timer = connection.cu.request()
            if status_or_timer != last_status_or_timer:
                if isinstance(status_or_timer, ControlUnit.Status):
                    status_observer.notify_status(status_or_timer)
                    last_status = status_or_timer
                elif isinstance(status_or_timer, ControlUnit.Timer):
                    app.logger.info("received new time from track")
                    time_observer.notify_timer(status_or_timer)
        except (eventlet.StopServe, greenlet.GreenletExit):
            app.logger.info("Received exeception. exit processing")
            return

        last_status_or_timer = status_or_timer
        sleep_time = calculate_sleep_time(last_status)
        eventlet.sleep(sleep_time)
    app.logger.info("finished listening, leaving event loop")


def track_listener_running():
    global track_listener_thread
    if track_listener_thread is None or track_listener_thread.dead:
        app.logger.info("TrackListener Thread finished execution. Message should have been provided.")
        track_listener_thread = None
    return track_listener_thread is not None


def start_track_listener(status_observer, time_observer):
    global track_listener_thread
    if track_listener_thread is None:
        app.logger.info("spawning listener thread")
        track_listener_thread = eventlet.spawn(listen, status_observer, time_observer)
        # sleep a little to allow thread to connect or finish
        time.sleep(0.1)
    return track_listener_running()


def stop_track_listener():
    global track_listener_thread
    if track_listener_thread is not None:
        app.logger.info("sending kill to listener thread")
        track_listener_thread.kill()
        track_listener_thread = None
