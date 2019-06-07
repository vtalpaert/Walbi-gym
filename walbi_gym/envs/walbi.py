from typing import TypeVar, List, Tuple, Sequence

import numpy as np
from gym import Env, spaces

import walbi_gym.communication.settings as _s
from walbi_gym.communication.settings import Message
from walbi_gym.communication import BaseInterface, SerialInterface


def constrain(x, in_min,  in_max, out_min, out_max, clip=False):
    if clip:
        x = max(in_min, min(in_max, x))
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


_DecimalList = TypeVar('DecimalList', np.ndarray, Sequence[float])


class WalbiEnv(Env):
    name = 'Walbi'
    version = _s.PROTOCOL_VERSION
    motor_ranges = _s.MOTOR_RANGES
    action_space = spaces.Box(low=-1, high=1, shape=_s.ACTION_SHAPE, dtype=np.float16)
    raw_action_space = spaces.Box(low=np.array(_s.RAW_ACTION_LOW), high=np.array(_s.RAW_ACTION_HIGH), dtype=np.int16)
    observation_space = spaces.Box(low=-1, high=1, shape=_s.OBSERVATION_SHAPE, dtype=np.float16)
    raw_observation_space = spaces.Box(low=np.array(_s.RAW_OBSERVATION_LOW), high=np.array(_s.RAW_OBSERVATION_HIGH), dtype=np.int16)
    reward_scale = _s.REWARD_SCALING
    reward_range = (-32.768, +32.767)  # linked to reward_scale

    def __init__(self, interface='serial', autoconnect=True, verify_version=True, *args, **kwargs):
        if interface == 'serial':
            self.interface = SerialInterface(*args, **kwargs)
        elif interface in ['bluetooth', 'wifi']:
            raise NotImplementedError('%s is not implemented yet' % interface)
        elif isinstance(interface, BaseInterface):
            self.interface = interface
        if autoconnect and not self.interface.is_connected:
            self.interface.connect()
        if verify_version and self.interface.verify_version():
            print('Version OK')

    def reset(self):
        self.interface.put_command(Message.RESET, expect_ok=True)
        observation, _, _, _ = self._receive_state()
        return observation

    def step(self, action: _DecimalList):
        self.interface.put_command(Message.STEP, expect_ok=True)
        self._send_action(action)
        observation, reward, done, info = self._receive_state()
        return observation, reward, done, info

    def _send_action(self, action: _DecimalList):
        self._send_raw_action(self._convert_action_float_to_int(action))

    @classmethod
    def _convert_action_float_to_int(cls, action: _DecimalList) -> List[Tuple[int, int]]:
        int16_action = [
            (
                int(constrain(
                    position,
                    cls.action_space.low[index][0],
                    cls.action_space.high[index][0],
                    cls.raw_action_space.low[index][0],
                    cls.raw_action_space.high[index][0]
                )),
                int(constrain(
                    span,
                    cls.action_space.low[index][1],
                    cls.action_space.high[index][1],
                    cls.raw_action_space.low[index][1],
                    cls.raw_action_space.high[index][1]
                ))
            ) for index, (position, span) in enumerate(action)]
        return int16_action

    def _send_raw_action(self, int16_action: Sequence):
        self.interface.put_command(Message.ACTION, param=int16_action, expect_ok=True)

    def _receive_state(self) -> Tuple[np.ndarray, float, bool, dict]:
        raw_observation, raw_reward, raw_termination, info = self._receive_raw_state()
        observation = self._convert_obs_int_to_float(raw_observation)
        reward, done = self._convert_reward_int_to_types(raw_reward, raw_termination)
        return observation, reward, done, info

    @classmethod
    def _convert_obs_int_to_float(cls, raw_obs: Sequence[int]) -> np.ndarray:
        obs = np.array([
            constrain(
                raw_value,
                cls.raw_observation_space.low[index],
                cls.raw_observation_space.high[index],
                cls.observation_space.low[index],
                cls.observation_space.high[index]
            ) for index, raw_value in enumerate(raw_obs)
        ], dtype=np.float16)
        return obs

    def _convert_reward_int_to_types(self, raw_reward: int, raw_termination: int) -> Tuple[float, bool]:
        return raw_reward / self.reward_scale, bool(raw_termination)

    def _receive_raw_state(self) -> Tuple[List[int], int, int, dict]:
        state = self.interface.expect_or_raise(Message.STATE)
        timestamp, raw_observation, raw_reward, raw_termination = state[0], state[1:11], state[11], state[12]
        return raw_observation, raw_reward, raw_termination, {'timestamp': timestamp}

    def _ask_state(self):
        self.interface.put_command(Message.STATE, expect_ok=True)
        return self._receive_state()

    def render(self, mode='human'):
        """TODO"""

    def close(self):
        print('Exiting...')
        self.interface.close()
