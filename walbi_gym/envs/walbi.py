from typing import TypeVar, List, Tuple, Sequence

import numpy as np
from gym import Env, spaces

from walbi_gym.protocol import Message, PROTOCOL_VERSION
from walbi_gym.communication import BaseInterface, make_interface
from walbi_gym.configuration import config
from walbi_gym.envs.utils import constrain_spaces


_DecimalList = TypeVar('DecimalList', np.ndarray, Sequence[float])
ObservationType = np.ndarray
ActionType = _DecimalList


class WalbiEnv(Env):
    name = 'Walbi'
    protocol_version = PROTOCOL_VERSION
    config = config
    action_space = spaces.Box(
        low=-1,
        high=1,
        shape=(10, 2),
        dtype=np.float16
    )
    raw_action_space = spaces.Box(
        low=np.array(list(zip(config['motors']['ranges']['positions']['low'], config['motors']['ranges']['span']['low']))),
        high=np.array(list(zip(config['motors']['ranges']['positions']['high'], config['motors']['ranges']['span']['high']))),
        dtype=np.int16
    )
    observation_space = spaces.Box(
        low=-1,
        high=1,
        shape=(10,),
        dtype=np.float16
    )
    raw_observation_space = spaces.Box(
        low=np.array(config['motors']['ranges']['positions']['low']),
        high=np.array(config['motors']['ranges']['positions']['high']),
        dtype=np.int16
    )

    def __init__(self, interface='serial', autoconnect=True, verify_version=True, *args, **kwargs):
        self.interface = make_interface(interface, *args, **kwargs)
        if autoconnect and not self.interface.is_connected:
            self.interface.connect()
        if verify_version and self.interface.is_connected and self.interface.verify_version():
            print('Version OK')

    def reset(self, return_interpretation: bool=False) -> ObservationType:
        self.interface.put_command(Message.RESET, expect_ok=True)
        state = self._receive_state()
        observation = self._state_to_observation(state)
        if not return_interpretation:
            return self._state_to_observation(state)
        else:
            reward, done, info = self._state_interpretation(state)
            return observation, reward, done, info

    def step(self, action: ActionType) -> Tuple[ObservationType, float, bool, dict]:
        int16_action = self._convert_action_float_to_int(action)
        self.interface.put_command(Message.STEP, param=int16_action, expect_ok=True)
        state = self._receive_state()
        observation = self._state_to_observation(state)
        reward, done, info = self._state_interpretation(state)
        return observation, reward, done, info

    def _send_action(self, action: ActionType):
        int16_action = self._convert_action_float_to_int(action)
        self.interface.put_command(Message.ACTION, param=int16_action, expect_ok=True)

    @classmethod
    def _convert_action_float_to_int(cls, action: ActionType) -> np.ndarray:
        return constrain_spaces(action, cls.action_space, cls.raw_action_space, clip=True)

    @classmethod
    def _convert_obs_int_to_float(cls, raw_obs: Sequence[int]) -> ObservationType:
        return constrain_spaces(raw_obs, cls.raw_observation_space, cls.observation_space, clip=False)

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

    def _state_to_observation(self, state) -> ObservationType:
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
        if self.interface.is_connected:
            self.interface.close()


if __name__ == '__main__':
    pass
