import time
import threading

import numpy as np
from gym import Env, spaces

from .robust_serial import *
from .threads import CommandThread, ListenerThread
from .utils import open_serial_port, constrain, CustomQueue, queue


class WalbiError(IOError):
    @staticmethod
    def receive_and_raise(f, expected_message):
        message = read_message(f)
        if message == Message.ERROR:
            error_code = read_i8(f)
            raise WalbiError('ERROR code %i' % error_code)
        elif message != expected_message:
            raise WalbiError('Expected %s but got %s' % (expected_message, message))


class WalbiEnv(Env):
    action_space = spaces.Box(low=-1, high=1, shape=(10, 2))
    observation_space = None
    motor_ranges = {
        0: ((0, 1000), (0, 30000)),
        1: ((0, 1000), (0, 30000)),
        2: ((0, 1000), (0, 30000)),
        3: ((0, 1000), (0, 30000)),
        4: ((0, 1000), (0, 30000)),
        5: ((0, 1000), (0, 30000)),
        6: ((0, 1000), (0, 30000)),
        7: ((0, 1000), (0, 30000)),
        8: ((0, 1000), (0, 30000)),
        9: ((0, 1000), (0, 30000)),
    }
    reward_scale = 1000
    reward_range = (-32.768, +32.767)  # linked to reward_scale

    def __init__(self, serial_port=None, baudrate=115200):
        self.is_connected = False
        self._obs = self._d = self._r = None
        try:
            self.serial_file = open_serial_port(serial_port=serial_port, baudrate=baudrate, timeout=None)
        except Exception as e:
            raise e
        self._connect()

        # Create Command queue for sending messages
        self.command_queue = CustomQueue(3)
        self.received_queue = CustomQueue(3)
        # Number of messages we can send to the Arduino without receiving an acknowledgment
        n_messages_allowed = 3
        self._n_received_semaphore = threading.Semaphore(n_messages_allowed)
        # Lock for accessing serial file (to avoid reading and writing at the same time)
        serial_lock = threading.Lock()

        # Event to notify threads that they should terminate
        self._exit_event = threading.Event()

        print('Starting Communication Threads')
        # Threads for arduino communication
        self._threads = [
            CommandThread(self, self.command_queue, self._exit_event, self._n_received_semaphore, serial_lock),
            ListenerThread(self, self.f, self._exit_event, self._n_received_semaphore, serial_lock)
        ]
        for t in self._threads:
            t.start()

    @property
    def f(self):
        return self.serial_file

    def _connect(self):
        # Initialize communication with Arduino
        while not self.is_connected:
            print('Waiting for arduino...')
            write_message(self.f, Message.CONNECT)
            bytes_array = bytearray(self.f.read(1))
            if not bytes_array:
                time.sleep(2)
                continue
            byte = bytes_array[0]
            if byte in (Message.CONNECT.value, Message.ALREADY_CONNECTED.value):
                self.is_connected = True
        print('Connected to Arduino')
        time.sleep(0.1)
        self.received_queue.clear()

    def _handle_message(self, message):
        if message == Message.OBSERVATION:
            raw_obs = [read_i16(self.f) for _ in self.motor_ranges]
            self.received_queue.put((message, raw_obs))
            self.command_queue.put((Message.OK, None))
        elif message == Message.REWARD:
            raw_r, raw_d = read_i16(self.f), read_i8(self.f)
            self.received_queue.put((message, (raw_r, raw_d)))
            self.command_queue.put((Message.OK, None))
        elif message == Message.OK:
            self.received_queue.put((Message.OK, None))
        elif message == Message.ERROR:
            error_code = read_i8(self.f)
            raise WalbiError('Received %s code %i' % (message, error_code))
        else:
            print('%s was not expected, ignored' % message)

    def _send_message(self, message, param):
        write_message(self.f, message)
        if message == Message.ACTION:
            for position, span in param:
                write_i16(self.f, position)
                write_i16(self.f, span)
        elif message == Message.CONFIG:
            raise NotImplementedError(str(message))
        if message != Message.OK:
            self.expect_or_raise(Message.OK)

    def expect_or_raise(self, expected_message, timeout=1):
        try:
            message, param = self.received_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            raise WalbiError('No message received within 1s (waiting for %s' % expected_message)
        if message != expected_message:
            raise WalbiError('Expected %s but got %s' % (expected_message, message))
        return param

    def reset(self):
        self.command_queue.put((Message.RESET, None))
        time.sleep(0.1)
        self._observation()
        return self._obs

    def step(self, action):
        self.command_queue.put((Message.STEP, None))
        time.sleep(0.1)
        self._action(action)
        time.sleep(0.1)
        self._observation()
        time.sleep(0.1)
        self._reward()
        time.sleep(0.1)
        return self._obs, self._r, self._d, {}

    def _action(self, action):
        int16_action = []
        for motor, ranges in self.motor_ranges.items():
            position_normalized, speed_normalized = action[motor]
            position = int(constrain(position_normalized, -1, 1, ranges[0][0], ranges[0][1]))
            span = int(constrain(speed_normalized, -1, 1, ranges[1][0], ranges[1][1]))
            int16_action.append((position, span))
        self.command_queue.put((Message.ACTION, int16_action))

    def _observation(self):
        raw_obs = self.expect_or_raise(Message.OBSERVATION)
        self._obs = np.array(raw_obs)
        return self._obs

    def _reward(self):
        raw_r, raw_d = self.expect_or_raise(Message.REWARD)
        self._r = raw_r / self.reward_range
        self._d = bool(raw_d)
        return self._r, self._d

    def render(self, mode='human'):
        """TODO"""

    def close(self):
        print('Exiting...')
        self.command_queue.clear()
        self.is_connected = False
        self._exit_event.set()
        self._n_received_semaphore.release()
        for t in self._threads:
            t.join()
        self.received_queue.clear()
        self.f.close()
