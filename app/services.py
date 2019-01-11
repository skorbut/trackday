import eventlet, serial

from flask_socketio import send, emit
from carreralib import ControlUnit
from app import app, socketio


def connect_control_unit(serial_port):
  cu = None
  while True:
    app.logger.info("Connecting Control Unit")

    try:
        cu = ControlUnit(serial_port)
        break
    except serial.serialutil.SerialException:
        app.logger.info("control unit not connected")
        socketio.emit('message', 'control_unit_not_connected', namespace='/track_events')
    eventlet.sleep(30)

  app.logger.info("control unit connected")
  socketio.emit('message', 'control_unit_connected', namespace='/track_events', broadcast=True)
  return cu
