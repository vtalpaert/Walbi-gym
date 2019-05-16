import time
import threading
from typing import Sequence


from .serial_utils import open_serial_port
from .robust_serial import *
from walbi_gym.communication.threads import CommandThread, ListenerThread, CustomQueue, queue
from walbi_gym.envs.errors import *
from walbi_gym.communication.settings import *


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


class SerialInterface(object):
    delay = 0.1  # delay for a message to be sent
    expect_or_raise_timeout = 1
    debug = False

    def __init__(self, serial_port=None, baudrate=115200):
        self.is_connected = False
        try:
            self.serial_file = open_serial_port(serial_port=serial_port, baudrate=baudrate, timeout=None)
        except Exception as e:
            raise e

        # Create Command queue for sending messages
        self._command_queue = CustomQueue(3)
        self._received_queue = CustomQueue(3)
        # Lock for accessing serial file (to avoid reading and writing at the same time)
        self._serial_lock = threading.Lock()
        # Event to notify threads that they should terminate
        self._exit_event = threading.Event()

        print('Starting Communication Threads')
        # Threads for arduino communication
        self._threads = [
            CommandThread(self, self._command_queue, self._exit_event, self._serial_lock),
            ListenerThread(self, self.serial_file, self._exit_event, self._serial_lock)
        ]
        for t in self._threads:
            t.start()

    def connect(self):
        # Initialize communication with Arduino
        while not self.is_connected:
            print('Waiting for Arduino...')
            self.put_command(Message.CONNECT)
            try:
                self.expect_or_raise_list((Message.CONNECT, Message.ALREADY_CONNECTED))
            except WalbiError:
                time.sleep(1)
                continue
            print('Connected to Arduino')
            self.is_connected = True
        time.sleep(2 * self.delay)
        self._received_queue.clear()
        try:  # if we still receive CONNECT, send that we consider ourselves ALREADY_CONNECTED
            self.expect_or_raise(Message.CONNECT)
            self.put_command(Message.ALREADY_CONNECTED)
        except WalbiError:
            pass
        time.sleep(1)
        self._received_queue.clear()

    def _handle_message(self, message):
        # Only called by threads respecting our _serial_lock
        if self.debug:
            print('Listener thread:', message, 'just in')
        if message in (Message.OBSERVATION, Message.REWARD, Message.ERROR):
            self._received_queue.put(
                (
                    message,
                    read_types(MESSAGE_TYPES[message], self.serial_file)
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
        write_message(self.serial_file, message)
        if message == Message.ACTION:
            for position, span in param:
                write_i16(self.serial_file, position)
                write_i16(self.serial_file, span)
        elif message == Message.CONFIG:
            raise NotImplementedError(str(message))

    def put_command(self, message, param=None, delay: bool = True, expect_ok: bool = False):
        self._command_queue.put((message, param))
        if delay:
            time.sleep(self.delay)
        if expect_ok:
            self.expect_or_raise(Message.OK)

    def expect_or_raise(self, expected_message: Message):
        return self.expect_or_raise_list([expected_message])

    def expect_or_raise_list(self, expected_messages: Sequence):
        if self.debug:
            print('expect', expected_messages)
        try:
            message, param = self._received_queue.get(block=True, timeout=self.expect_or_raise_timeout)
        except queue.Empty as e:
            raise WalbiTimeoutError(self.expect_or_raise_timeout, expected_messages) from e
        if message == Message.ERROR:
            raise WalbiArduinoError(int(param))
        if message not in expected_messages:
            raise WalbiUnexpectedMessageError('Expected %s but got %s' % (expected_messages, message))
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
        self.serial_file.close()
