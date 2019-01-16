import os, sys, eventlet, serial, json
eventlet.monkey_patch()

from flask_socketio import send, emit
from carreralib import ControlUnit
from app import app, socketio, db

from app.models import Race, Lap

control_unit_connection_thread = None


def connect_control_unit(serial_port):
  while True:
    app.logger.info("Connecting Control Unit...")

    try:
        cu = ControlUnit(serial_port)
        version = cu.version
        app.logger.info("...connected to Control Unit Version: {}", repr(version))
        break
    except serial.serialutil.SerialException:
        app.logger.info("control unit not connected")
        socketio.emit('status', 'not_connected', namespace='/control_unit_events')
    eventlet.sleep(30)

  app.logger.info("returning Control Unit")
  socketio.emit('status', 'connected', namespace='/control_unit_events')
  return cu;

def handle_control_unit_events(serial_port):
  cu = connect_control_unit(serial_port)
  last_status = None
  current_race = Race.current()
  if current_race.status == 'created':
    current_race.start
    db.session.add(current_race)
    db.session.commit()
    app.logger.info("sending reset to control unit")
    cu.reset()
    app.logger.info("sending start to control unit")
    cu.start()
  while True:
    try:
      status_or_timer = cu.request()
      event_name = type(status_or_timer).__name__
      if 'Status' == event_name:
        app.logger.info("processing a status " + repr(status_or_timer))
        if last_status != status_or_timer:
          socketio.emit('fuel_levels', json.dumps(status_or_timer.fuel), namespace='/fuel_events')
          socketio.emit('pit_status', json.dumps(status_or_timer.pit), namespace='/pit_events')
          socketio.emit('startlight_status', status_or_timer.start, namespace='/start_light_status')
        else:
          app.logger.info('status has not changed, not reporting')
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
    except serial.serialutil.SerialException:
        app.logger.info("control unit disconnected")
        socketio.emit('status', 'disconnected', namespace='/control_unit_events')
        cu = connect_control_unit(serial_port)




def try_control_unit_connection():
  global control_unit_connection_thread
  if control_unit_connection_thread is None:
    app.logger.info('Initializing cu listener thread')
    serial_port = os.getenv('SERIAL_PORT')

    if not serial_port:
      print('SERIAL_PORT is not defined')
      sys.exit(1)

    control_unit_connection_thread = eventlet.spawn(handle_control_unit_events, serial_port)
  else:
    app.logger.info('control_unit_connection thread is already created')