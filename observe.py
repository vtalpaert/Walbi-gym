import time

import gym
import walbi_gym


if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        while True:
            state = walbi._ask_state()
            print(state)
            input()
            walbi.step([[0, 0]]*10)
