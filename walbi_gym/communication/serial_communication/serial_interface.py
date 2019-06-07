import time

import serial

from .serial_utils import open_serial_port
import walbi_gym.communication.settings as _s
from walbi_gym.communication.base import BaseInterface


class SerialInterface(BaseInterface):
    def __init__(self, serial_port=None, baudrate=115200):
        try:
            self.file = open_serial_port(serial_port=serial_port, baudrate=baudrate, timeout=None)
        except Exception as e:
            raise e
        super(SerialInterface, self).__init__()

    def _read_byte(self):
        try:
            bytes_array = bytearray(self.file.read(1))
        except serial.SerialException:
            time.sleep(_s.RATE)
            return None
        if not bytes_array:
            time.sleep(_s.RATE)
            return None
        byte = bytes_array[0]
        return byte
