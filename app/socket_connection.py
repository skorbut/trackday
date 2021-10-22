import json
from app import socketio


def emit_status(status):
    socketio.emit('fuel_levels', json.dumps(status.fuel), namespace='/fuel_events')
    socketio.emit('pit_status', json.dumps(status.pit), namespace='/pit_events')
    socketio.emit('startlight_status', status.start, namespace='/startlight_events')


def emit_pit_stops(pit_stops):
    pit_stop_counts = list(map(lambda pit_stop: pit_stop.stops, pit_stops))
    socketio.emit('pit_stops', json.dumps(pit_stop_counts), namespace='/pit_events')


def emit_lap(timer, timing):
    socketio.emit('lap_finished', json.dumps({'controller': timer.address,
                                              'lap_number': timing.laps,
                                              'lap_time': timing.lap_time,
                                              'best_time': timing.best_time}), namespace='/lap_events')


def emit_cu_status(message, serial_port):
    [message, serial_port]
    socketio.emit('status', ' to '.join([message, serial_port]), namespace='/control_unit_events')


def emit_race_finished(race_id):
    socketio.emit('race_finished', race_id, namespace='/race_events')
