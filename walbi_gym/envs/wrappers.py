import typing

from ruamel.yaml import YAML
import numpy as np
from gym import Wrapper

from .walbi import WalbiEnv

yaml = YAML()   # typ='safe', if not specfied, is 'rt' (round-trip)


class Transition(typing.NamedTuple):
    observation: np.float16
    action: np.float16
    next_observation: np.float16
    reward: float
    terminal: bool
    agent_info: dict
    env_info: dict


class RawTransition(typing.NamedTuple):
    raw_observation: np.int16
    raw_action: np.int16
    next_raw_observation: np.int16
    reward: float
    terminal: bool
    agent_info: dict
    env_info: dict


T = typing.TypeVar('T', Transition, RawTransition)


class RecordWrapper(Wrapper):
    def __init__(self, env, save_to: str):
        self.save_to = save_to
        self._last_observation = None
        self.transitions: typing.List[Transition] = []
        super(RecordWrapper, self).__init__(env)

    def step(self, action):
        next_observation, reward, done, info = self.env.step(action)
        self.transitions.append(
            Transition(
                self._last_observation,
                action,
                next_observation,
                reward,
                done,
                {},
                info
            )
        )
        self._last_observation = next_observation
        return next_observation, reward, done, info

    def reset(self, **kwargs):
        self._last_observation = self.env.reset(**kwargs)
        return self._last_observation

    def close(self):
        dump_transitions(self.transitions, self.save_to)
        return self.env.close()


def dump_transitions(transitions: typing.Sequence[T], filename, to_dict=True):
    data = {'transitions': []}
    for t in transitions:
        d = t._asdict()
        if to_dict:
            d = dict(d)
        for k, v in d.items():
            if isinstance(v, np.ndarray):
                d[k] = v.tolist()
        if isinstance(t, Transition):
            name = 'transition'
        elif isinstance(t, RawTransition):
            name = 'raw_transition'
        else:
            name = 'data'
        data['transitions'].append({name: d})
    with open(filename, 'w') as f:
        yaml.dump(data, f)


def load_transitions(filename) -> typing.Sequence[T]:
    with open(filename) as f:
        data = yaml.load(f)
    transitions = []
    for d in data['transitions']:
        if 'transition' in d:
            t = d['transition']
            for k, v in t.items():
                if isinstance(v, list):
                    t[k] = np.array(v, dtype=np.float16)
                elif isinstance(v, dict):
                    t[k] = dict(v)
            transitions.append(Transition(**t))
        elif 'raw_transition' in d:
            t = d['raw_transition']
            for k, v in t.items():
                if isinstance(v, list):
                    t[k] = np.array(v, dtype=np.float16)
                elif isinstance(v, dict):
                    t[k] = dict(v)
            transitions.append(RawTransition(**t))
    return transitions


if __name__ == '__main__':
    filename = 'test.yaml'

    def _random_transition():
        return Transition(
            observation=WalbiEnv.observation_space.sample(),
            action=WalbiEnv.action_space.sample(),
            next_observation=WalbiEnv.observation_space.sample(),
            reward=np.random.uniform(*WalbiEnv.reward_range),
            terminal=bool(np.random.randint(0, 2)),
            agent_info={'debug': 'test'},
            env_info={'debug': 'test'}
        )

    def _random_raw_transition():
        return RawTransition(
            raw_observation=WalbiEnv.raw_observation_space.sample(),
            raw_action=WalbiEnv.raw_action_space.sample(),
            next_raw_observation=WalbiEnv.raw_observation_space.sample(),
            reward=np.random.uniform(*WalbiEnv.reward_range),
            terminal=bool(np.random.randint(0, 2)),
            agent_info={'debug': 'test'},
            env_info={'debug': 'test'}
        )

    transitions_generated = [_random_transition() for _ in range(2)]
    dump_transitions(transitions_generated, filename)
    transitions_loaded = load_transitions(filename)
    for tg, tl in zip(transitions_generated, transitions_loaded):
        print(tg)
        print(tl)
