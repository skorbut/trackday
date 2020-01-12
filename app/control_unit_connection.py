import eventlet
import serial

from app import app
from app.socket_connection import emit_cu_status
from carreralib import ControlUnit, connection


def connect():
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
        except serial.serialutil.SerialException:
            emit_cu_status('not_connected', serial_port)
        except connection.TimeoutError:
            emit_cu_status('timeout', serial_port)

        counter += 1
        eventlet.sleep(5)

    emit_cu_status('connected', serial_ports[counter % 5])
    return cu
