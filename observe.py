import time

import gym
import walbi_gym


if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        walbi.debug = True
        while True:
            obs = walbi._ask_observation()
            print('[', ','.join(map(str, obs)), ']')
            input()
