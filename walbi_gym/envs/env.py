from typing import TypeVar, List, Tuple, Sequence

import numpy as np
from gym import Env, spaces

from walbi_gym.configuration import config
from walbi_gym.envs.utils import constrain_spaces
from walbi_gym.walbi import Walbi


_DecimalList = TypeVar('DecimalList', np.ndarray, Sequence[float])
ObservationType = np.ndarray
ActionType = _DecimalList


class WalbiEnv(Env):
    name = 'Walbi'
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

    def __init__(self, *args, **kwargs):
        self.walbi = Walbi(*args, **kwargs)

    def reset(self, return_interpretation: bool=False) -> ObservationType:
        state = self.walbi.get_last_state()
        observation = self._state_to_observation(state)
        if not return_interpretation:
            return self._state_to_observation(state)
        else:
            reward, done, info = self._state_interpretation(state)
            return observation, reward, done, info

    def step(self, action: ActionType) -> Tuple[ObservationType, float, bool, dict]:
        self._send_action(action)
        state = self.walbi.get_last_state()
        observation = self._state_to_observation(state)
        reward, done, info = self._state_interpretation(state)
        return observation, reward, done, info

    def _send_action(self, action: ActionType):
        int16_action = self._convert_action_norm_to_raw(action)
        self.walbi.send_action(int16_action)

    @classmethod
    def _convert_action_norm_to_raw(cls, action: ActionType) -> np.ndarray:
        return constrain_spaces(action, cls.action_space, cls.raw_action_space, clip=True)
    
    @classmethod
    def _convert_obs_norm_to_raw(cls, obs: ObservationType) -> np.ndarray:
        return constrain_spaces(obs, cls.observation_space, cls.raw_observation_space, clip=False)

    @classmethod
    def _convert_obs_raw_to_norm(cls, raw_obs: Sequence[int]) -> ObservationType:
        return constrain_spaces(raw_obs, cls.raw_observation_space, cls.observation_space, clip=False)

    def _state_interpretation(self, state) -> Tuple[float, bool, dict]:
        """Calculates reward and termination. Provides the info dict"""
        timestamp = state[0]
        is_position_updated = [bool(state[update_flag_index]) for update_flag_index in range(2, 21, 2)]
        reward, termination = 0, False  # TODO
        info = {'timestamp': timestamp, 'is_position_updated': is_position_updated}
        return reward, termination, info

    def _state_to_observation(self, state) -> ObservationType:
        raw_observation = [state[position_index] for position_index in range(1, 20, 2)]
        observation = self._convert_obs_raw_to_norm(raw_observation)
        return observation

    def render(self, mode='human'):
        """TODO"""

    def close(self):
        print('Exiting...')
        self.walbi.close()


if __name__ == '__main__':
    pass
