import eventlet
import serial

from app import app
from app.socket_connection import emit_cu_status
from carreralib import ControlUnit, connection


def connect():
    app.logger.info("Entering control_unit_connection#connect")
    serial_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/tty.usbserial']
    counter = 0
    while True:
        serial_port = serial_ports[counter % 5]
        app.logger.info("Connecting Control Unit..." + str(serial_port))

        try:
            cu = ControlUnit(serial_port, timeout=0.1)
            version = cu.version()
            app.logger.info("...connected to Control Unit Version: {}", repr(version))
            break
        except serial.serialutil.SerialException as e:
            app.logger.info("Control unit not connected to Raspberry due to " + str(e))
            emit_cu_status('not_connected', serial_port)
        except connection.TimeoutError:
            app.logger.info("Timeout while trying to connect control unit to " + serial_port)
            emit_cu_status('timeout', serial_port)

        counter += 1
        eventlet.sleep(5)

    app.logger.info("returning Control Unit")
    emit_cu_status('connected', serial_ports[counter % 5])
    app.logger.info("leaving control_unit_connection#connect")
    return cu
