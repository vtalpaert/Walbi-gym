import time

import serial

from .serial_utils import open_serial_port
from .robust_serial import *
from walbi_gym.envs.errors import *
from walbi_gym.communication.settings import *
from walbi_gym.communication.base import Interface


MAP_TYPE_READ = {
    'int8': read_i8,
    'int16': read_i16,
    'int32': read_i32,
}
MAP_TYPE_WRITE = {
    'int8': write_i8,
    'int16': write_i16,
    'int32': write_i32,
}


def read_types(type_list, file):
    try:
        return [MAP_TYPE_READ[t](file) for t in type_list]
    except KeyError:
        raise WalbiCommunicationError('%s has an invalid type' % str(type_list))


def write_types(): pass  # TODO


class SerialInterface(Interface):
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
            time.sleep(RATE)
            return None
        if not bytes_array:
            time.sleep(RATE)
            return None
        byte = bytes_array[0]
        return byte

    def _handle_message(self, message):
        # Only called by threads respecting our _serial_lock
        if self.debug:
            print('Listener thread:', message, 'just in')
        if message in (Message.OBSERVATION, Message.REWARD, Message.ERROR):
            self._received_queue.put(
                (
                    message,
                    read_types(MESSAGE_TYPES[message], self.file)
                )
            )
            self.put_command(Message.OK)
        elif message in (Message.CONNECT, Message.ALREADY_CONNECTED, Message.OK):
            self._received_queue.put((message, None))
        else:
            print('%s was not expected, ignored' % message)

    def _send_message(self, message, param):
        # Only called by threads respecting our _serial_lock
        if self.debug:
            print('Command thread: sent', message)
        write_message(self.file, message)
        if message == Message.ACTION:
            for position, span in param:
                write_i16(self.file, position)
                write_i16(self.file, span)
        elif message == Message.CONFIG:
            raise NotImplementedError(str(message))
