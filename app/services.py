import os, sys, eventlet, serial, json, datetime
eventlet.monkey_patch()

from flask_socketio import send, emit
from carreralib import ControlUnit
from random import randint, getrandbits
from app import app, socketio, db

from app.models import Race, Lap

control_unit_connection_thread = None

class Timing(object):
  def __init__(self, num):
    self.num = num
    self.time = None
    self.lap_time = None
    self.best_time = None
    self.laps = 0

  def newlap(self, timer):
    if self.time is not None:
      self.lap_time = timer.timestamp - self.time
      if self.best_time is None or self.lap_time < self.best_time:
        self.best_time = self.lap_time
      self.laps += 1
    self.time = timer.timestamp

def connect_control_unit(serial_port):
  while True:
    app.logger.info("Connecting Control Unit...")

    try:
        cu = ControlUnit(serial_port, timeout=0.1)
        version = cu.version
        app.logger.info("...connected to Control Unit Version: {}", repr(version))
        break
    except serial.serialutil.SerialException:
        app.logger.info("Control unit not connected to Raspberry")
        socketio.emit('status', 'not_connected', namespace='/control_unit_events')
    except carreralib.connection.TimeoutError
        app.logger.info("Timeout while trying to connect control unit")
        socketio.emit('status', 'Timeout', namespace='/control_unit_events')

    eventlet.sleep(10)

  app.logger.info("returning Control Unit")
  socketio.emit('status', 'connected', namespace='/control_unit_events')
  return cu;

def handle_control_unit_events(serial_port):
  cu = connect_control_unit(serial_port)
  last_status_or_timer = None
  current_race = Race.current()
  timings = [Timing(num) for num in range(0, 8)]
  timeouts = 0
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
      if status_or_timer == last_status_or_timer:
        continue
      if isinstance(status_or_timer, ControlUnit.Status):
        app.logger.info("processing a status " + repr(status_or_timer))
        socketio.emit('fuel_levels', json.dumps(status_or_timer.fuel), namespace='/fuel_events')
        socketio.emit('pit_status', json.dumps(status_or_timer.pit), namespace='/pit_events')
        socketio.emit('startlight_status', status_or_timer.start, namespace='/start_light_status')
      elif isinstance(status_or_timer, ControlUnit.Timer):
        timing = timings[status_or_timer.address]
        timing.newlap(status_or_timer)
        lap = Lap(race_id = current_race.id, controller = status_or_timer.address, time = timing.lap_time)
        db.session.add(lap)
        db.session.commit()
        socketio.emit('lap_finished', json.dumps({'controller': status_or_timer.address, 'lap_number': timing.laps, 'lap_time': timing.lap_time, 'best_time': timing.best_time}), namespace='/lap_events')
        app.logger.info("new lap " + repr(lap))
      last_status_or_timer = status_or_timer
      timeouts = 0
      eventlet.sleep(0.3)
    except serial.serialutil.SerialException:
        app.logger.info("control unit disconnected, exiting loop")
        socketio.emit('status', 'disconnected', namespace='/control_unit_events')
        cu = connect_control_unit(serial_port)
    except carreralib.connection.TimeoutError
        app.logger.info("Timeout while retrieving status from control unit({})", repr(timeouts))
        socketio.emit('status', 'Timeout', namespace='/control_unit_events')
        timeouts += 1

def mock_control_unit_events(serial_port):
  current_race = Race.current()
  if current_race.status == 'created':
    current_race.start
  while True:
    if randint(0,100) % 2 == 0:
      app.logger.info("mocking a status change")
      status_type_rand = randint(0, 100)
      if status_type_rand % 3 == 0:
        socketio.emit('fuel_levels', json.dumps([randint(0,15), randint(0,15), randint(0,15), randint(0,15), randint(0,15), randint(0,15), randint(0,15), randint(0,15)]), namespace='/fuel_events')
      elif status_type_rand % 3 == 1:
        socketio.emit('pit_status', json.dumps([bool(getrandbits(1)), bool(getrandbits(1)), bool(getrandbits(1)), bool(getrandbits(1)), bool(getrandbits(1)), bool(getrandbits(1)), bool(getrandbits(1)), bool(getrandbits(1))]), namespace='/pit_events')
      else:
        socketio.emit('startlight_status', 4, namespace='/start_light_status')

    else:
      app.logger.info("mocking a lap")
      socketio.emit('lap_finished', json.dumps({'controller': randint(0,7), 'lap_number': randint(0,100), 'lap_time': randint(32000, 64000), 'best_time': randint(32000, 64000)}), namespace='/lap_events')
    eventlet.sleep(randint(0, 9))


def mock_control_unit_connection():
  global control_unit_connection_thread

  if not control_unit_connection_thread is None:
    control_unit_connection_thread.kill()
    control_unit_connection_thread = None

  control_unit_connection_thread = eventlet.spawn(mock_control_unit_events, 'not needed here')


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

def disconnect_control_unit():
  global control_unit_connection_thread
  if not control_unit_connection_thread is None:
    app.logger.info('disconnecting Control Unit...')
    control_unit_connection_thread.kill()
    control_unit_connection_thread = None
    app.logger.info('control_unit_connection thread killed')
