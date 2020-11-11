import serial
import time

from app import app
from app.socket_connection import emit_cu_status
from carreralib import ControlUnit, connection


class ControlUnitConnection:
    def __init__(self):
        self.cu = None
        self.connect()

    def connect(self):
        serial_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/tty.usbserial']
        for serial_port in serial_ports:
            app.logger.info("trying " + str(serial_port))

            try:
                self.cu = ControlUnit(serial_port, timeout=0.1)
                app.logger.info(" connected to Control Unit Version {0} using serial port {1}".format(str(self.cu.version()), serial_port))
                break
            except serial.serialutil.SerialException:
                emit_cu_status('not_connected', serial_port)
            except connection.TimeoutError:
                emit_cu_status('timeout', serial_port)
        app.logger.info(" not connected")

    def connected(self):
        if self.cu is None:
            return False
        try:
            version = self.cu.version()
            app.logger.info("connected to Control Unit Version: {0}".format(str(version)))
        except serial.serialutil.SerialException:
            emit_cu_status('not_connected')
            return False
        except connection.TimeoutError:
            emit_cu_status('timeout')
            return False
        return True

    def reset(self):
        for n in range(3):
            try:
                self.cu.reset()
                self.cu.start()
                return True
            except connection.TimeoutError:
                app.logger.error("Timeout while resetting track")
                time.sleep(0.1)

    def cu(self):
        return self.cu
