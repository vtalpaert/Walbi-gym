import numpy as np


from .walbi import WalbiEnv
from .simulated import LX16A


class WalbiMockEnv(WalbiEnv):
    _time = 0
    refresh_period = 0.2  # [s] interval between to steps
    reward_range = (-1, 1)

    def __init__(self, *args, **kwargs):
        self.sample_obs()

    def sample_obs(self):
        self.raw_observation = self.raw_observation_space.sample()
        self._motors = [LX16A(initial_position=raw_obs) for raw_obs in self.raw_observation]

    @property
    def observation(self):
        return self._convert_obs_raw_to_norm(self.raw_observation)

    def reset(self, return_interpretation: bool=False):
        self.sample_obs()
        if not return_interpretation:
            return self.observation
        else:
            reward = np.random.uniform(*self.reward_range)
            terminal = bool(np.random.binomial(1, 0.1))  # p=0.1
            info = {'debug': 'mock', 'timestamp': self._time}
            return self.observation, reward, terminal, info

    def step(self, action):
        self._time += self.refresh_period
        raw_action = self._convert_action_norm_to_raw(action)
        for i in range(len(self._motors)):
            self.raw_observation[i] = self._motors[i].step(dt=self.refresh_period, target_encoder=raw_action[i, 0])
        reward = np.random.uniform(*self.reward_range)
        terminal = bool(np.random.binomial(1, 0.1))  # p=0.1
        info = {'debug': 'mock', 'timestamp': self._time}
        return self.observation, reward, terminal, info

    def close(self):
        pass
