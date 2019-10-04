import numpy as np
import gym
import walbi_gym
import time

import matplotlib.pyplot as plt
from ruamel.yaml import YAML

yaml = YAML()   # typ='safe', if not specfied, is 'rt' (round-trip)


def get_pos(walbi, dim):
    state = walbi._ask_state()
    return state[0], state[1 + 2 * dim]


if __name__ == '__main__':
    plot_dim = 0
    time_limit = 3000  # [ms]
    filename = 'identification.yaml'

    times, positions = [], []

    with gym.make('Walbi-v0') as walbi:
        # choose an action
        target_raw = walbi.raw_action_space.sample()
        target_norm = walbi._convert_action_raw_to_norm(target_raw)

        # ask walbi to hold whatever position he had
        state = walbi._ask_state()
        obs = walbi._state_to_observation(state)
        action = np.zeros((10, 2))
        action[:, 0] = obs
        action[:, 1] = -0.5
        walbi._send_action(action)
        time.sleep(0.1)

        ts, position = get_pos(walbi, plot_dim)
        walbi._send_action(target_norm)
        while ts < time_limit:
            ts, position = get_pos(walbi, plot_dim)
            times.append(ts)
            positions.append(position)
    
    plt.plot(times, [target_raw[plot_dim]] * len(time), 'bo')
    plt.plot(times, positions)

     with open(filename, 'w') as f:
        yaml.dump({'times': time, 'positions': positions}, f)
