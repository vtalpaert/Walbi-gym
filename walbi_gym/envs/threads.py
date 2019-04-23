import threading
import time
import weakref

import serial

from .robust_serial import Message
from .utils import queue

rate = 1 / 2000  # 2000 Hz (limit the rate of communication with the arduino)


class CommandThread(threading.Thread):
    """
    Thread that send messages to the arduino
    :param parent: will call _send_message on parent (WalbiEnv object)
    :param command_queue: (Queue)
    :param exit_event: (Threading.Event object)
    :param serial_lock: (threading.Lock)
    """

    def __init__(self, parent, command_queue, exit_event, serial_lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.parent = weakref.proxy(parent)
        self.command_queue = command_queue
        self.exit_event = exit_event
        self.serial_lock = serial_lock

    def run(self):
        while not self.exit_event.is_set():
            if self.exit_event.is_set():
                break
            try:
                message, param = self.command_queue.get_nowait()
            except queue.Empty:
                time.sleep(rate)
                continue

            with self.serial_lock:
                self.parent._send_message(message, param)
            time.sleep(rate)
        print('Command Thread Exited')


class ListenerThread(threading.Thread):
    """
    Thread that listen to the Arduino
    It is used to add send_tokens to the n_received_semaphore
    :param parent: will call _handle_message on parent (WalbiEnv object)
    :param exit_event: (threading.Event object)
    :param serial_lock: (threading.Lock)
    """

    def __init__(self, parent, serial_file, exit_event, serial_lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.parent = weakref.proxy(parent)
        self.serial_file = serial_file
        self.exit_event = exit_event
        self.serial_lock = serial_lock

    def run(self):
        while not self.exit_event.is_set():
            try:
                bytes_array = bytearray(self.serial_file.read(1))
            except serial.SerialException:
                time.sleep(rate)
                continue
            if not bytes_array:
                time.sleep(rate)
                continue
            byte = bytes_array[0]
            with self.serial_lock:
                try:
                    message = Message(byte)
                except ValueError:
                    continue
                self.parent._handle_message(message)
            time.sleep(rate)
        print('Listener Thread Exited')
