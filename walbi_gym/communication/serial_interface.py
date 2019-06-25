import time
import sys
import glob

import serial

from walbi_gym.envs.errors import WalbiError
import walbi_gym.envs.definitions as _s  # settings
from walbi_gym.communication.base import BaseInterface


# From https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def get_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    results = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            results.append(port)
        except (OSError, serial.SerialException):
            pass
    return results


def open_serial_port(serial_port=None, baudrate=115200, timeout=0, write_timeout=0):
    # Open serial port (for communication with Arduino)
    if serial_port is None:
        ports = get_serial_ports()
        if len(ports) == 0:
            raise WalbiError('No serial port found')
        serial_port = get_serial_ports()[0]
    # timeout=0 non-blocking mode, return immediately in any case, returning zero or more,
    # up to the requested number of bytes
    return serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout, writeTimeout=write_timeout)


class SerialInterface(BaseInterface):
    def __init__(self, serial_port=None, baudrate=115200):
        try:
            self.file = open_serial_port(serial_port=serial_port, baudrate=baudrate, timeout=None)
        except Exception as e:
            raise e
        super(SerialInterface, self).__init__()
