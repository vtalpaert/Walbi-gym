import time

from enum import IntEnum
from gym import Env, spaces
import numpy as np

from .robust_serial import *
from .utils import open_serial_port, constrain


class Message(IntEnum):
    """
    Pre-defined messages
    """
    CONNECT = 0
    ALREADY_CONNECTED = 1
    RESET = 2
    STEP = 9
    ACTION = 3
    OBSERVATION = 4
    REWARD = 5  # reward and termination
    CLOSE = 6
    CONFIG = 7
    ERROR = 8


def read_message(f):
    """
    :param f: file handler or serial file
    :return: (Message Enum Object)
    """
    return Message(read_i8(f))


def write_message(f, message):
    """
    :param f: file handler or serial file
    :param message: (Message Enum Object)
    """
    write_i8(f, message.value)


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

    def __init__(self, serial_port=None):
        self.is_connected = False
        self._obs = None
        try:
            self.serial_file = open_serial_port(serial_port=serial_port, baudrate=115200, timeout=None)
        except Exception as e:
            raise e
        self._connect()

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
            if byte in [Message.CONNECT.value, Message.ALREADY_CONNECTED.value]:
                self.is_connected = True
        print('Connected to Arduino')

    def reset(self):
        write_message(self.f, Message.RESET)
        return self._observation()

    def step(self, action):
        write_message(self.f, Message.STEP)
        self._action(action)
        return self._observation(), *self._reward(), {}

    def _action(self, action):
        write_message(self.f, Message.ACTION)
        for motor, ranges in self.motor_ranges.items():
            position_normalized, speed_normalized = action[motor]
            position = constrain(position_normalized, -1, 1, ranges[0][0], ranges[0][1])
            speed = constrain(speed_normalized, -1, 1, ranges[1][0], ranges[1][1])
            write_i16(self.f, position)
            write_i16(self.f, speed)

    def _observation(self):
        WalbiError.receive_and_raise(self.f, Message.OBSERVATION)
        self._obs = np.array((read_i16(self.f) for _ in self.motor_ranges))
        return self._obs

    def _reward(self):
        WalbiError.receive_and_raise(self.f, Message.REWARD)
        reward = read_i16(self.f) / self.reward_range
        done = bool(read_i8(self.f))
        return reward, done

    def render(self, mode='human'):
        """TODO"""

    def close(self):
        self.is_connected = False
        self.f.close()


if __name__ == '__main__':
    walbi = WalbiEnv()
    print('reset', walbi.reset())
    for _ in range(10):
        action = walbi.action_space.sample()
        print('action', action)
        print('step', walbi.step(action))
