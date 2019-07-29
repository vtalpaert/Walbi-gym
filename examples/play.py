import numpy as np
import gym
import walbi_gym
import time

positions = []

if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        for position in positions:
            action = np.zeros((10, 2))
            action[:, 0] = np.array(position)
            action[:, 1] = 1
            walbi.step(action)
            time.sleep(0.5)
