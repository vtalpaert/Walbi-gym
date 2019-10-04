import gym
import walbi_gym
import time

if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        walbi.debug = True
        print('reset', walbi.reset())
        for _ in range(50):
            action = walbi.action_space.sample() / 4
            action[:, 1] = -0.8
            print('action', action)
            print('step', walbi.step(action))
            time.sleep(0.5)
