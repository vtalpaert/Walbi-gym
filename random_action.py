import gym
import walbi_gym

if __name__ == '__main__':
    with gym.make('Walbi-v0') as walbi:
        walbi.debug = True
        print('reset', walbi.reset())
        for _ in range(10):
            action = walbi.action_space.sample() / 4
            print('action', action)
            print('step', walbi.step(action))
