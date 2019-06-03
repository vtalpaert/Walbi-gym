import numpy as np

from .walbi import WalbiEnv


class WalbiMockEnv(WalbiEnv):
    def __init__(self, *args, **kwargs):
        pass

    def reset(self):
        return self.observation_space.sample()

    def step(self, action):
        observation = self.observation_space.sample()
        reward = np.random.uniform(*self.reward_range)
        terminal = bool(np.random.binomial(1, 0.1))  # p=0.1
        info = {'debug': 'mock'}
        return observation, reward, terminal, info

    def close(self):
        pass
