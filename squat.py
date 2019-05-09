import numpy as np
import gym
import walbi_gym
import time

if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        standing = np.array([-0.4055, -0.1287, -0.3137, 0.10394, 0.1702, 0.5757, 0.0248, 0.1698, 0.31, -0.1848])
        squat = np.array([-0.873, -0.505, 0.4731, -0.3765, 0.4036, 1.015, -0.05786, -0.543, 0.4187, -0.4387])
        positions = [standing, squat]
        i = 0
        while True:
            action = np.zeros((10, 2))
            action[:, 0] = positions[i]
            action[:, 1] = 1
            walbi.step(action)
            i = (i + 1) % 2
            time.sleep(0.5)
