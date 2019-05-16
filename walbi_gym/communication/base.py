from abc import ABC
import threading
import time
from typing import Sequence

from walbi_gym.communication.threads import CommandThread, ListenerThread, CustomQueue, queue
from walbi_gym.envs.errors import *
from walbi_gym.communication.settings import *


class Interface(ABC):
    delay = 0.1  # delay for a message to be sent
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

    def _send_message(self, message, param):
        raise NotImplementedError

    def _handle_message(self, message):
        raise NotImplementedError

    def _read_byte(self):
        raise NotImplementedError

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
        self.file.close()
