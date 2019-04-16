from gym.envs.registration import register

register(
    id='Walbi-v0',
    entry_point='walbi_gym.envs:WalbiEnv',
)
