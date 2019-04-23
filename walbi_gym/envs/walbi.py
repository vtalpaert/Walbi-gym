import time
import threading

import numpy as np
from gym import Env, spaces

from .robust_serial import *
from .threads import CommandThread, ListenerThread
from .utils import open_serial_port, constrain, CustomQueue, queue


class WalbiError(IOError):
    pass


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
    delay = 0.1
    expect_or_raise_timeout = 2
    debug = False

    def __init__(self, serial_port=None, baudrate=115200):
        self.is_connected = False
        self._obs = self._d = self._r = None
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
            ListenerThread(self, self.f, self._exit_event, self._serial_lock)
        ]
        for t in self._threads:
            t.start()

        self._connect()

    @property
    def f(self):
        return self.serial_file

    def _connect(self):
        # Initialize communication with Arduino
        time.sleep(self.delay)
        while not self.is_connected:
            print('Waiting for Arduino...')
            self.put_command(Message.CONNECT)
            #self.command_queue.put((Message.CONNECT, None))
            time.sleep(self.delay)
            try:
                self.expect_or_raise_list((Message.CONNECT, Message.ALREADY_CONNECTED))
            except WalbiError:
                time.sleep(1)
                continue
            print('Connected to Arduino')
            self.is_connected = True
        time.sleep(self.delay)
        self._received_queue.clear()
        try:
            self.expect_or_raise(Message.CONNECT)
            self.put_command(Message.ALREADY_CONNECTED)
        except WalbiError:
            pass
        time.sleep(1)
        self._received_queue.clear()

    def _handle_message(self, message):
        if self.debug:
            print(message, 'just in')
        if message == Message.OBSERVATION:
            raw_obs = [read_i16(self.f) for _ in self.motor_ranges]
            self._received_queue.put((message, raw_obs))
            self.put_command(Message.OK)
        elif message == Message.REWARD:
            raw_r, raw_d = read_i16(self.f), read_i8(self.f)
            self._received_queue.put((message, (raw_r, raw_d)))
            self.put_command(Message.OK)
        elif message == Message.ERROR:
            error_code = read_i8(self.f)
            self._received_queue.put((message, error_code))
        elif message in (Message.CONNECT, Message.ALREADY_CONNECTED, Message.OK):
            self._received_queue.put((message, None))
        else:
            print('%s was not expected, ignored' % message)

    def _send_message(self, message, param):
        if self.debug:
            print('write', message)
        write_message(self.f, message)
        if message == Message.ACTION:
            for position, span in param:
                write_i16(self.f, position)
                write_i16(self.f, span)
        elif message == Message.CONFIG:
            raise NotImplementedError(str(message))

    def put_command(self, message, param=None):
        self._command_queue.put((message, param))

    def expect_or_raise(self, expected_message: Message):
        return self.expect_or_raise_list([expected_message])

    def expect_or_raise_list(self, expected_messages: (list, tuple)):
        if self.debug:
            print('expect', expected_messages)
        try:
            message, param = self._received_queue.get(block=True, timeout=self.expect_or_raise_timeout)
        except queue.Empty:
            raise WalbiError(
                'Timeout: no message received within %fs (waiting for %s)'
                % (self.expect_or_raise_timeout, list(map(str, expected_messages)))
            )
        if message == Message.ERROR:
            raise WalbiError('Received %s code %i' % (message, param))
        if message not in expected_messages:
            raise WalbiError('Expected %s but got %s' % (expected_messages, message))
        if self.debug:
            print('got %s as expected (param %s)' % (message, str(param)))
        return param

    def reset(self):
        self.put_command(Message.RESET)
        time.sleep(self.delay)
        self.expect_or_raise(Message.OK)
        time.sleep(self.delay)
        self._observation()
        return self._obs

    def step(self, action):
        self.put_command(Message.STEP)
        time.sleep(self.delay)
        self.expect_or_raise(Message.OK)
        self._action(action)
        time.sleep(self.delay)
        self._observation()
        time.sleep(self.delay)
        self._reward()
        return self._obs, self._r, self._d, {}

    def _action(self, action):
        int16_action = []
        for motor, ranges in self.motor_ranges.items():
            position_normalized, speed_normalized = action[motor]
            position = int(constrain(position_normalized, -1, 1, ranges[0][0], ranges[0][1]))
            span = int(constrain(speed_normalized, -1, 1, ranges[1][0], ranges[1][1]))
            int16_action.append((position, span))
        self.put_command(Message.ACTION, int16_action)

    def _observation(self):
        raw_obs = self.expect_or_raise(Message.OBSERVATION)
        self._obs = np.array(raw_obs)
        return self._obs

    def _ask_observation(self):
        self.put_command(Message.OBSERVATION)
        time.sleep(self.delay)
        return self._observation()

    def _reward(self):
        raw_r, raw_d = self.expect_or_raise(Message.REWARD)
        self._r = raw_r / self.reward_range
        self._d = bool(raw_d)
        return self._r, self._d

    def _ask_reward(self):
        self.put_command(Message.REWARD)
        time.sleep(self.delay)
        return self._reward()

    def render(self, mode='human'):
        """TODO"""

    def close(self):
        print('Exiting...')
        self._exit_event.set()
        self._command_queue.clear()
        self.is_connected = False
        for t in self._threads:
            t.join(timeout=0.1)
        self._received_queue.clear()
        self.f.close()
