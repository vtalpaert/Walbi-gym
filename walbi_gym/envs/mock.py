import numpy as np


from .walbi import WalbiEnv


class WalbiMockEnv(WalbiEnv):
    _time = 0
    reward_range = (-1, 1)

    def __init__(self, *args, **kwargs):
        self.observation = self.observation_space.sample()

    def reset(self, return_interpretation: bool=False):
        self.observation = self.observation_space.sample()
        if not return_interpretation:
            return self.observation
        else:
            reward = np.random.uniform(*self.reward_range)
            terminal = bool(np.random.binomial(1, 0.1))  # p=0.1
            info = {'debug': 'mock', 'timestamp': self._time}
            return self.observation, reward, terminal, info

    def step(self, action):
        self._time += 0.2
        self.observation = 0.2 * self.observation + 0.8 * action[:, 0]
        reward = np.random.uniform(*self.reward_range)
        terminal = bool(np.random.binomial(1, 0.1))  # p=0.1
        info = {'debug': 'mock', 'timestamp': self._time}
        return self.observation, reward, terminal, info

    def close(self):
        pass
