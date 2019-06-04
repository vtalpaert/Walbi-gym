import typing
import time
import os.path
from os import makedirs

from ruamel.yaml import YAML
import numpy as np
from gym import Wrapper


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
    file_format = '-%Y-%m-%d-%H-%M.yaml'

    def __init__(self, env, save_to_folder: str):
        self.save_to = save_to_folder
        self.step_counter = 0
        self._last_observation = None
        self.transitions: typing.List[Transition] = []
        super().__init__(env)

    def step(self, action, agent_info=None):  # pylint: disable=E0202
        if agent_info is None:
            agent_info = {}
        next_observation, reward, done, env_info = self.env.step(action)
        env_info['step'] = self.step_counter  # step goes to env_info rather than agent_info
        self.transitions.append(
            Transition(
                self._last_observation,
                action,
                next_observation,
                reward,
                done,
                agent_info,
                env_info
            )
        )
        self.step_counter += 1
        self._last_observation = next_observation
        return next_observation, reward, done, env_info

    def reset(self, **kwargs):  # pylint: disable=E0202
        self._last_observation = self.env.reset(**kwargs)
        self.step_counter = 0
        return self._last_observation

    def close(self):
        self.flush()
        return self.env.close()

    def flush(self):
        makedirs(self.save_to, exist_ok=True)
        savename = self._get_name() + time.strftime(self.file_format)
        savepath = os.path.join(self.save_to, savename)
        dump_transitions(self.transitions, savepath)
        self.transitions = []

    def _get_name(self):
        try:
            return self.env.spec.id
        except AttributeError:
            pass
        try:
            return self.env.name + '-v' + str(self.env.version)
        except AttributeError:
            return 'Env'


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
    import gym
    import walbi_gym

    with RecordWrapper(gym.make('WalbiMock-v0'), 'test') as env:
        env.reset()
        for _ in range(20):
            action = env.action_space.sample()
            _, _, done, _ = env.step(action)
            if done:
                env.reset()
