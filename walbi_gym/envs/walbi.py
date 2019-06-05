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
    version = _s.VERSION
    motor_ranges = _s.MOTOR_RANGES
    action_space = spaces.Box(low=-1, high=1, shape=_s.ACTION_SHAPE, dtype=np.float16)
    raw_action_space = spaces.Box(low=np.array(_s.RAW_ACTION_LOW), high=np.array(_s.RAW_ACTION_HIGH), dtype=np.int16)
    observation_space = spaces.Box(low=-1, high=1, shape=_s.OBSERVATION_SHAPE, dtype=np.float16)
    raw_observation_space = spaces.Box(low=np.array(_s.RAW_OBSERVATION_LOW), high=np.array(_s.RAW_OBSERVATION_HIGH), dtype=np.int16)
    reward_scale = 1000
    reward_range = (-32.768, +32.767)  # linked to reward_scale

    def __init__(self, interface='serial', autoconnect=True, *args, **kwargs):
        self._obs = self._d = self._r = None

        if interface == 'serial':
            self.interface = SerialInterface(*args, **kwargs)
        elif interface in ['bluetooth', 'wifi']:
            raise NotImplementedError('%s is not implemented yet' % interface)
        elif isinstance(interface, BaseInterface):
            self.interface = interface
        if autoconnect and not self.interface.is_connected:
            self.interface.connect()

    def reset(self):
        self.interface.put_command(Message.RESET, expect_ok=True)
        self._observation()
        return self._obs

    def step(self, action: _DecimalList):
        self.interface.put_command(Message.STEP, expect_ok=True)
        self._action(action)
        self._observation()
        self._reward()
        return self._obs, self._r, self._d, {}

    def _action(self, action: _DecimalList):
        self._raw_action(self._convert_action_float_to_int(action))

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

    def _raw_action(self, int16_action: Sequence[Tuple[int, int]]):
        self.interface.put_command(Message.ACTION, param=int16_action, expect_ok=True)

    def _observation(self):
        raw_obs = self._raw_observation()
        self._obs = self._convert_obs_int_to_float(raw_obs)
        return self._obs

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

    def _raw_observation(self) -> List[int]:
        return self.interface.expect_or_raise(Message.OBSERVATION)

    def _ask_observation(self):
        self.interface.put_command(Message.OBSERVATION, expect_ok=False)
        return self._observation()

    def _reward(self, raw=False) -> Tuple[float, bool]:
        raw_r, raw_d = self._raw_reward()
        self._r, self._d = self._convert_reward_int_to_types(raw_r, raw_d)
        return self._r, self._d

    def _convert_reward_int_to_types(self, raw_reward: int, raw_termination: int) -> Tuple[float, bool]:
        return raw_reward / self.reward_scale, bool(raw_termination)

    def _raw_reward(self) -> Tuple[int, int]:
        return self.interface.expect_or_raise(Message.REWARD)

    def _ask_reward(self):
        self.interface.put_command(Message.REWARD, expect_ok=False)
        return self._reward()
    
    def _ask_timestamp_observation(self):
        self.interface.put_command(Message.TIMESTAMP_OBSERVATION, expect_ok=False)
        return self.interface.expect_or_raise(Message.TIMESTAMP_OBSERVATION)


    def render(self, mode='human'):
        """TODO"""

    def close(self):
        print('Exiting...')
        self.interface.close()
