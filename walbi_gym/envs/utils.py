from __future__ import print_function, division, absolute_import

import sys
import glob

import serial


# From https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def get_serial_ports():
    """
    Lists serial ports.


    :return: ([str]) A list of available serial ports
    """
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
    """
    Try to open serial port with Arduino
    If not port is specified, it will be automatically detected

    :param serial_port: (str)
    :param baudrate: (int)
    :param timeout: (int) None -> blocking mode
    :param write_timeout: (int)
    :return: (Serial Object)
    """
    # Open serial port (for communication with Arduino)
    if serial_port is None:
        serial_port = get_serial_ports()[0]
    # timeout=0 non-blocking mode, return immediately in any case, returning zero or more,
    # up to the requested number of bytes
    return serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout, writeTimeout=write_timeout)


def constrain(x, in_min,  in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
