import numpy as np
import gym
import walbi_gym
import time
from itertools import count

if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        state = walbi._ask_state()
        obs = walbi._state_to_observation(state)
        action = np.zeros((10, 2))
        action[:, 0] = obs
        action[:, 1] = -0.5
        last_ts = state[0]
        for epoch in count():
            obs, _, _, info = walbi.step(action)
            timestamp = info['timestamp']
            nb_received_position = sum(info['is_position_updated'])
            delta = timestamp - last_ts
            last_ts = timestamp
            print('delta', delta, 'error rate', 100 * (1 - nb_received_position / (10 * epoch)), '%')
