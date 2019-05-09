import numpy as np
import gym
import walbi_gym
import time

if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        pos1 = np.array([0.04672, -0.0495, 0.435, 0.3477, 1.054, 0.1295, 0.0248, -0.5767, -0.1783, -1.0625])
        pos2 = np.array([0.04672, -0.0396, -0.4038, 0.3477, 1.051, 0.1295, 0.04132, -0.929, -0.1783, -1.064])
        pos3 = np.array([1.015, -0.0396, -0.338, 0.3477, 1.054, -1.316, 0.04132, -0.929, -3.72, -1.0625])
        pos4 = np.array([1.019, -0.05942, 0.8477, 0.3477, 1.051, -1.32, 0.04132, 0.3882, -0.1783, -1.0625])
        positions = [pos1, pos2, pos3, pos4]
        i = 0
        while True:
            action = np.zeros((10, 2))
            action[:, 0] = positions[i]
            action[:, 1] = 1
            walbi.step(action)
            i = (i + 1) % 4
            time.sleep(0.5)
