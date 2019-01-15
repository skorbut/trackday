import os, sys, eventlet, serial
eventlet.monkey_patch()

from flask_socketio import send, emit
from carreralib import ControlUnit
from app import app, socketio

from app.models import Race, Lap

control_unit_connection_thread = None

def connect_control_unit(serial_port):
  cu = None
  last_status = None
  current_race = Race.current()
  # try to connect to control unit
  while True:
    app.logger.info("Connecting Control Unit...")

    try:
        cu = ControlUnit(serial_port)
        app.logger.info("sending reset to control unit")
        cu.reset()
        app.logger.info("sending start to control unit")
        cu.start()
        break
    except serial.serialutil.SerialException:
        app.logger.info("control unit not connected")
        socketio.emit('status', 'not_connected', namespace='/control_unit_events')
    eventlet.sleep(30)

  app.logger.info("...connected to Control Unit")
  socketio.emit('status', 'connected', namespace='/control_unit_events')

  while True:
    # process events from control unit
    status_or_timer = cu.request()
    event_name = type(status_or_timer).__name__
    if 'Status' == event_name:
      if last_status != status_or_timer:
        socketio.emit('fuel_levels', status_or_timer.fuel, namespace='/fuel_events')
        socketio.emit('pit_status', status_or_timer.pit, namespace='/pit_events')
        socketio.emit('startlight_status', status_or_timer.start, namespace='/start_light_status')
      last_status = status_or_timer
    elif 'Timer' == event_name:
      # store lap
      lap = Lap(race_id = current_race.id, controller = status_or_timer.address, time = status_or_timer.timestamp)
      db.session.add(lap)
      db.session.commit()
      socketio.emit('lap_finished', lap, namespace='/lap_events')
      app.logger.info("new lap " + repr(lap))
    else:
      app.logger.info("unknown event received: %s" % event_name)
    eventlet.sleep(0.1)




def try_control_unit_connection():
  global control_unit_connection_thread
  if control_unit_connection_thread is None:
    app.logger.info('Initializing cu listener thread')
    serial_port = os.getenv('SERIAL_PORT')

    if not serial_port:
      print('SERIAL_PORT is not defined')
      sys.exit(1)

    control_unit_connection_thread = eventlet.spawn(connect_control_unit, serial_port)
  else:
    app.logger.info('control_unit_connection thread is already created')