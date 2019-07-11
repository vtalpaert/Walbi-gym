from gym import Wrapper
from gym import spaces


class GoalWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.observation_space = spaces.Dict({
            'observation': env.observation_space,
            'achieved_goal': None,
            'desired_goal': None,
        })


