from typing import TypeVar, List, Tuple, Sequence

import numpy as np
from gym import Env, spaces

import walbi_gym.envs.definitions as _s  # settings
from walbi_gym.envs.definitions import Message
from walbi_gym.communication import BaseInterface, make_interface


def constrain(x, in_min,  in_max, out_min, out_max, clip=False):
    if clip:
        x = max(in_min, min(in_max, x))
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


_DecimalList = TypeVar('DecimalList', np.ndarray, Sequence[float])
Observation = np.ndarray
Action = _DecimalList


class WalbiEnv(Env):
    name = 'Walbi'
    version = _s.PROTOCOL_VERSION
    motor_ranges = _s.MOTOR_RANGES
    action_space = spaces.Box(low=-1, high=1, shape=_s.ACTION_SHAPE, dtype=np.float16)
    raw_action_space = spaces.Box(low=np.array(_s.RAW_ACTION_LOW), high=np.array(_s.RAW_ACTION_HIGH), dtype=np.int16)
    observation_space = spaces.Box(low=-1, high=1, shape=_s.OBSERVATION_SHAPE, dtype=np.float16)
    raw_observation_space = spaces.Box(low=np.array(_s.RAW_OBSERVATION_LOW), high=np.array(_s.RAW_OBSERVATION_HIGH), dtype=np.int16)

    def __init__(self, interface='serial', autoconnect=True, verify_version=True, *args, **kwargs):
        self.interface = make_interface(interface, *args, **kwargs)
        if autoconnect and not self.interface.is_connected:
            self.interface.connect()
        if verify_version and self.interface.verify_version():
            print('Version OK')

    def reset(self) -> Observation:
        self.interface.put_command(Message.RESET, expect_ok=True)
        state = self._receive_state()
        return self._state_to_observation(state)

    def step(self, action: Action) -> Tuple[Observation, float, bool, dict]:
        int16_action = self._convert_action_float_to_int(action)
        self.interface.put_command(Message.STEP, param=int16_action, expect_ok=True)
        state = self._receive_state()
        observation = self._state_to_observation(state)
        reward, done, info = self._state_interpretation(state)
        return observation, reward, done, info

    def _send_action(self, action: Action):
        int16_action = self._convert_action_float_to_int(action)
        self.interface.put_command(Message.ACTION, param=int16_action, expect_ok=True)

    @classmethod
    def _convert_action_float_to_int(cls, action: Action) -> List[Tuple[int, int]]:
        int16_action = [
            (
                int(constrain(
                    position,
                    cls.action_space.low[index][0],
                    cls.action_space.high[index][0],
                    cls.raw_action_space.low[index][0],
                    cls.raw_action_space.high[index][0],
                    clip=True
                )),
                int(constrain(
                    span,
                    cls.action_space.low[index][1],
                    cls.action_space.high[index][1],
                    cls.raw_action_space.low[index][1],
                    cls.raw_action_space.high[index][1],
                    clip=True
                ))
            ) for index, (position, span) in enumerate(action)]
        return int16_action

    @classmethod
    def _convert_obs_int_to_float(cls, raw_obs: Sequence[int]) -> Observation:
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

    def _state_interpretation(self, state) -> Tuple[float, bool, dict]:
        """Calculates reward and termination. Provides the info dict"""
        timestamp = state[0]
        is_position_updated = [bool(state[update_flag_index]) for update_flag_index in range(2, 21, 2)]
        reward, termination = 0, False  # TODO
        info = {'timestamp': timestamp, 'is_position_updated': is_position_updated}
        return reward, termination, info

    def _receive_state(self):
        state = self.interface.expect_or_raise(Message.STATE)
        return state

    def _state_to_observation(self, state) -> Observation:
        raw_observation = [state[position_index] for position_index in range(1, 20, 2)]
        observation = self._convert_obs_int_to_float(raw_observation)
        return observation

    def _ask_state(self):
        self.interface.put_command(Message.STATE, expect_ok=True)
        return self._receive_state()

    def render(self, mode='human'):
        """TODO"""

    def close(self):
        print('Exiting...')
        self.interface.close()
