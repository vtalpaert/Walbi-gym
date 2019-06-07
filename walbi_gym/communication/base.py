from abc import ABC
import threading
import time

import serial
import socket

from walbi_gym.communication.threads import CommandThread, ListenerThread, CustomQueue, queue
from walbi_gym.envs import errors
import walbi_gym.communication.settings as _s
from walbi_gym.communication.settings import Message
from walbi_gym.communication import robust_serial


MAP_TYPE_READ = {
    'int8': robust_serial.read_i8,
    'int16': robust_serial.read_i16,
    'int32': robust_serial.read_i32,
}
MAP_TYPE_WRITE = {
    'int8': robust_serial.write_i8,
    'int16': robust_serial.write_i16,
    'int32': robust_serial.write_i32,
}


def read_types(type_list, file):
    try:
        return [MAP_TYPE_READ[t](file) for t in type_list]
    except KeyError:
        raise errors.WalbiCommunicationError('%s has an invalid type' % str(type_list))


def write_types(type_list, data, file):
    """data can be a list of types [t1, t2] or list of list of types [[t1, t2], [t1, t2]]"""
    try:
        for t, value in zip(type_list, data):
            if isinstance(t, str):
                MAP_TYPE_WRITE[t](file, value)
            else:  # assume second case
                for sub_t, sub_value in zip(t, value):
                    MAP_TYPE_WRITE[sub_t](file, sub_value)
    except KeyError:
        raise errors.WalbiCommunicationError('%s has an invalid type' % str(type_list))


class BaseInterface(ABC):
    delay = 0.1  # delay for a message to be sent # TODO test lower
    expect_or_raise_timeout = 1
    debug = False
    file = None
    is_connected = False

    def __init__(self):
        # Create Command queue for sending messages
        self._command_queue = CustomQueue(3)
        self._received_queue = CustomQueue(3)
        # Lock for accessing serial file (to avoid reading and writing at the same time)
        self._lock = threading.Lock()
        # Event to notify threads that they should terminate
        self._exit_event = threading.Event()

        print('Starting Communication Threads')
        # Threads for arduino communication
        self._threads = [
            CommandThread(self, self._command_queue, self._exit_event, self._lock),
            ListenerThread(self, self.file, self._exit_event, self._lock)
        ]
        for t in self._threads:
            t.start()

    def connect(self):
        # Initialize communication with Arduino
        while not self.is_connected:
            self.put_command(Message.CONNECT)
            try:
                self.expect_or_raise(Message.CONNECT)
            except errors.WalbiUnexpectedMessageError as e:
                if e.received_message == Message.ALREADY_CONNECTED:
                    print('Arduino already connected')
                else:
                    raise e from e
            except errors.WalbiError:
                print('Waiting for Arduino...')
                time.sleep(1)
                continue
            print('Connected to Arduino')
            self.is_connected = True
        time.sleep(2 * self.delay)
        self._received_queue.clear()
        try:  # if we still receive CONNECT, send that we consider ourselves ALREADY_CONNECTED
            self.expect_or_raise(Message.CONNECT)
            self.put_command(Message.ALREADY_CONNECTED)
        except errors.WalbiError:
            pass
        time.sleep(0.5)
        self._received_queue.clear()

    def verify_version(self):
        self.put_command(Message.VERSION, param=_s.PROTOCOL_VERSION, expect_ok=True)
        arduino_version = self.expect_or_raise(Message.VERSION)
        if arduino_version != _s.PROTOCOL_VERSION:
            raise errors.WalbiProtocolVersionError()
        return True
    
    def _read_byte(self):
        try:
            bytes_array = bytearray(self.file.read(1))
        except (serial.SerialException, socket.error):
            time.sleep(_s.RATE)
            return None
        if not bytes_array:
            time.sleep(_s.RATE)
            return None
        byte = bytes_array[0]
        return byte

    def _handle_message(self, message):
        # Only called by threads respecting our _serial_lock
        if self.debug:
            print('Listener thread:', message, 'just in')
        if message in (Message.STATE, Message.ERROR):
            try:
                self._received_queue.put(
                    (
                        message,
                        read_types(_s.MESSAGE_TYPES[message], self.file)
                    )
                )
            except KeyError as e:
                raise NotImplementedError(str(message)) from e
            self.put_command(Message.OK)
        elif message in (Message.CONNECT, Message.ALREADY_CONNECTED, Message.OK):
            self._received_queue.put((message, None))
        else:
            print('%s was not expected, ignored' % message)

    def _send_message(self, message, param):
        # Only called by threads respecting our _serial_lock
        if self.debug:
            print('Command thread: sent', message)
        robust_serial.write_message(self.file, message)
        if param is not None:
            try:
                write_types(_s.MESSAGE_TYPES[message], param, self.file)
            except KeyError as e:
                raise NotImplementedError(str(message)) from e

    def put_command(self, message, param=None, delay: bool = True, expect_ok: bool = False):
        self._command_queue.put((message, param))
        if delay:
            time.sleep(self.delay)
        if expect_ok:
            self.expect_or_raise(Message.OK)

    def expect_or_raise(self, expected_message: Message):
        if self.debug:
            print('expect', expected_message)
        try:
            message, param = self._received_queue.get(block=True, timeout=self.expect_or_raise_timeout)
        except queue.Empty as e:
            raise errors.WalbiTimeoutError(self.expect_or_raise_timeout, expected_message) from e
        if message == Message.ERROR:
            raise errors.WalbiArduinoError(int(param))
        if message != expected_message:
            raise errors.WalbiUnexpectedMessageError(message, expected_message=expected_message)
        if self.debug:
            print('got %s as expected (param %s)' % (message, str(param)))
        return param

    def close(self):
        print('Closing serial communication...')
        self._exit_event.set()
        self._command_queue.clear()
        self.is_connected = False
        for t in self._threads:
            t.join(timeout=0.1)
        self._received_queue.clear()
        self.file.close()
