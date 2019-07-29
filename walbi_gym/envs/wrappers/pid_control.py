from typing import Sequence, Tuple

import numpy as np

from gym import ActionWrapper
from gym import spaces

from pid_controller.pid import PID

from walbi_gym.envs.utils import _clip


class PidWrapper(ActionWrapper):
    _nb_motors = 10
    last_observation = None
    last_timestamp = None
    last_action = None  # is the action ultimately sent

    def __init__(self, env, K: Sequence[Tuple[float, float, float]]):
        assert isinstance(env.action_space, spaces.Box)
        assert env.action_space.shape == (self._nb_motors, 2)
        self.action_space = spaces.Box(low=env.action_space.low[:, 0], high=env.action_space.high[:, 0])
        assert self.action_space.shape == (self._nb_motors,)
        self.pids = [PID(p=K[i][0], i=K[i][1], d=K[i][2], get_time=lambda: 0) for i in range(self._nb_motors)]
        self.env = env
        self.observation_space = env.observation_space
        self.reward_range = env.reward_range
        self.metadata = env.metadata
        self.spec = getattr(env, 'spec', None)

    def reset(self, **kwargs):
        return_interpretation = kwargs.pop('return_interpretation', False)
        observation, reward, done, info = self.env.reset(return_interpretation=True, **kwargs)
        self.last_observation = observation
        self.last_timestamp = info['timestamp']
        if return_interpretation:
            return observation, reward, done, info
        else:
            return observation

    def step(self, action, clip=True, tolerance=0.002):
        self.last_action = self.action(action, clip=clip, tolerance=tolerance)
        observation, reward, done, info = self.env.step(self.last_action)
        self.last_observation = observation
        self.last_timestamp = info['timestamp']  # [ms]
        return observation, reward, done, info

    def action(self, action, clip, tolerance):
        """creates new action avoiding """
        new_action = np.zeros((self._nb_motors, 2))
        new_action[:, 0] = action
        new_action[:, 1] = self.env.action_space.low[:, 1]  # the highest speed is the lowest span
        for i, pid in enumerate(self.pids):
            curr_tm = self.last_timestamp / 1000  # [s]
            feedback = self.last_observation[i]
            pid.target = action[i] if abs(pid.target - feedback) > tolerance else feedback  # errors under tolerance are ignored
            new_action[i, 0] = feedback - pid(feedback=self.last_observation[i], curr_tm=curr_tm)
        if clip:
            return self.clip(new_action)
        else:
            return new_action

    def action_target(self):
        """returns the action state we are aiming for"""
        return np.array([pid.target for pid in self.pids], dtype=self.action_space.dtype)

    def clip(self, action, dim=0):
        for i, x in enumerate(action):
            action[i, dim] = _clip(x[dim], self.env.action_space.low[i, dim], self.env.action_space.high[i, dim])
        return action

if __name__ == '__main__':
    import gym
    import walbi_gym
    from walbi_gym.envs import WalbiMockEnv
    import matplotlib.pyplot as plt

    K = [(0.8, 0, 0.0001)] * 10
    steps = 10000

    plot_dim = 0
    time, target, sent, position, error = [], [], [], [], []
    with PidWrapper(gym.make('WalbiMock-v0'), K) as env:
        env.reset()
        for step in range(steps):
            action = env.action_space.sample() if step % 200 == 0 else action
            observation, _, done, info = env.step(action, clip=False)
            raw_observation = WalbiMockEnv._convert_obs_norm_to_raw(observation)
            action_target = - np.ones((10,2))
            action_target[:, 0] = env.action_target()
            raw_action_target = WalbiMockEnv._convert_action_norm_to_raw(action_target)
            raw_action_sent = WalbiMockEnv._convert_action_norm_to_raw(env.last_action)
            time.append(info['timestamp'])
            target.append(float(raw_action_target[plot_dim, 0]))
            sent.append(raw_action_sent[plot_dim, 0])
            position.append(raw_observation[plot_dim])
            if done:
                pass #env.reset()

    plt.plot(time, target, 'bo')
    plt.plot(time, position)
    plt.plot(time, sent)
    plt.show()
