import time

import gym
import walbi_gym


if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        while True:
            obs, _, _, _ = walbi._ask_state()
            print('[', ','.join(map(str, obs)), ']')
            input()
