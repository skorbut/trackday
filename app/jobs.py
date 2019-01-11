import eventlet
eventlet.monkey_patch()

import os, sys
from app import app, services

@app.before_first_request
def try_control_unit_connection():
  app.logger.info('Initializing cu listener thread')
  serial_port = os.getenv('SERIAL_PORT')

  if not serial_port:
    print('SERIAL_PORT is not defined')
    sys.exit(1)

  eventlet.spawn(services.connect_control_unit, serial_port)
