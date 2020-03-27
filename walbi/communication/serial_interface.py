import time
import sys
import glob

import serial

from walbi.errors import WalbiError
from walbi.configuration import config
from walbi.communication.base import BaseInterface


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


class SerialInterface(BaseInterface):
    def __init__(self, serial_port='auto', baudrate=None):
        if baudrate is None:
            baudrate = config['communication']['baud_rate']
        if serial_port == 'auto':
            ports = get_serial_ports()
            if len(ports) == 0:
                raise WalbiError('No serial port found')
            serial_port = get_serial_ports()[0]
        try:
            # timeout=0 non-blocking mode, return immediately in any case, returning zero or more,
            # up to the requested number of bytes
            self.file = serial.Serial(port=serial_port, baudrate=baudrate, timeout=0, writeTimeout=0)
        except Exception as e:
            raise e
        super(SerialInterface, self).__init__()
