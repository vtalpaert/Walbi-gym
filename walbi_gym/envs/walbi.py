import time
import threading
from typing import TypeVar, List, Tuple, Sequence

import numpy as np
from gym import Env, spaces

from .robust_serial import *
from .threads import CommandThread, ListenerThread
from .utils import open_serial_port, constrain, CustomQueue, queue
from .errors import *


DecimalList = TypeVar('DecimalList', np.ndarray, Sequence[float])


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
    delay = 0.1  # delay for a message to be sent
    expect_or_raise_timeout = 1
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
        # Only called by threads respecting our _serial_lock
        if self.debug:
            print('write', message)
        write_message(self.f, message)
        if message == Message.ACTION:
            for position, span in param:
                write_i16(self.f, position)
                write_i16(self.f, span)
        elif message == Message.CONFIG:
            raise NotImplementedError(str(message))

    def put_command(self, message, param=None, delay: bool=True, expect_ok: bool=False):
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

    def reset(self):
        self.put_command(Message.RESET, expect_ok=True)
        self._observation()
        return self._obs

    def step(self, action: DecimalList):
        self.put_command(Message.STEP, expect_ok=True)
        self._action(action)
        self._observation()
        self._reward()
        return self._obs, self._r, self._d, {}

    def _action(self, action: DecimalList):
        self._raw_action(self._convert_action_float_to_int(action))

    def _convert_action_float_to_int(self, action: DecimalList) -> List[int]:
        int16_action = []
        for motor, ranges in self.motor_ranges.items():
            position_normalized, speed_normalized = action[motor]
            position = int(constrain(position_normalized, -1, 1, ranges[0][0], ranges[0][1]))
            span = int(constrain(speed_normalized, -1, 1, ranges[1][0], ranges[1][1]))
            int16_action.append((position, span))
        return int16_action

    def _raw_action(self, int16_action: Sequence[int]):
        self.put_command(Message.ACTION, param=int16_action)

    def _observation(self):
        raw_obs = self._raw_observation()
        self._obs = self._convert_obs_int_to_float(raw_obs)
        return self._obs

    def _convert_obs_int_to_float(self, raw_obs: Sequence[int]) -> np.ndarray:
        # TODO
        return np.array(raw_obs)

    def _raw_observation(self) -> List[int]:
        return self.expect_or_raise(Message.OBSERVATION)

    def _ask_observation(self):
        self.put_command(Message.OBSERVATION, expect_ok=False)
        return self._observation()

    def _reward(self) -> Tuple[float, bool]:
        raw_r, raw_d = self._raw_reward()
        self._r, self._d = self._convert_reward_int_to_types(raw_r, raw_d)
        return self._r, self._d

    def _convert_reward_int_to_types(self, raw_reward: int, raw_termination: int) -> Tuple[float, bool]:
        return raw_reward / self.reward_scale, bool(raw_termination)

    def _raw_reward(self) -> Tuple[int, int]:
        return self.expect_or_raise(Message.REWARD)

    def _ask_reward(self):
        self.put_command(Message.REWARD, expect_ok=False)
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
