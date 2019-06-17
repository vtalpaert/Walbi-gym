import numpy as np
import gym
import walbi_gym
import time


def print_position(obs):
    print('[', ','.join(map(str, obs)), ']')


def print_positions(obs_list):
    print('[')
    for obs in obs_list:
        print('[', ','.join(map(str, obs)), '],')
    print(']')


def record_one_position(walbi):
    input('cut power and move walbi')
    obs = walbi._ask_observation()
    action = np.zeros((10, 2))
    action[:, 0] = obs
    action[:, 1] = 1
    time.sleep(0.1)
    obs, _, _, info = walbi.step(action)
    print(info)
    accepted = bool(input('is position valid ? (0 or empty if no)')
    if accepted:
        print_position(obs)
        return obs
    else:
        return record_one_position(walbi)


if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        walbi = walbi_gym.envs.wrappers.RecordWrapper(walbi, save_to_folder='saves')
        positions = []
        try:
            while True:
                positions.append(obs)
        finally:
            print_positions(positions)
