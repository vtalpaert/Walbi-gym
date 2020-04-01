#!/usr/bin/env python

import numpy as np
import os
import math as m
import gym
from gym import spaces
import pybullet as p
from diy_gym import DIYGym
from diy_gym.addons.addon import Addon, AddonFactory
from diy_gym.addons.sensors.object_state_sensor import ObjectStateSensor


def normalize(value, low, high):
    """Responsible for a smooth gradient between penality and reward
    Maps the value supposedly between low and high towards -2..2 (because thanh at 2 is almost 1)"""
    return m.tanh(4 / (high - low) * (value - high) + 2)


class VelocityReward(Addon):
    """Positive reward between 0 and upper_limit"""
    def __init__(self, parent, config):
        super(VelocityReward, self).__init__(parent, config)
        self.uid = parent.uid
        self.multiplier = config.get('multiplier', 1.0)
        self.axis = config.get('axis', 0)
        self.upper_limit = config.get('upper_limit', 2)  # [m/s]

    def reward(self):
        velocity_on_axis = p.getBaseVelocity(self.uid)[0][self.axis]
        # encourage with a clear gradient (1) to go forward
        return self.multiplier * normalize(velocity_on_axis, - self.upper_limit, self.upper_limit)


class PoiseReward(Addon):
    """PoiseReward positively rewards a good 'position' in z and pitch, and respectively negatively by using a smooth tanh transition"""
    def __init__(self, parent, config):
        super(PoiseReward, self).__init__(parent, config)
        self.uid = parent.uid
        self.initial_pose = p.getBasePositionAndOrientation(self.uid)

        self.terminal_penality = config.get('terminal_penality', 0)  # a positive value that is substracted to the reward if terminal
        self.multiplier_position = config.get('multiplier_position', 1.0)
        self.multiplier_rotation = config.get('multiplier_position', 1.0)
        self.position_limit = config.get('position_limit', 0.2)  # [m]
        self.position_sensibility = config.get('position_sensibility', 0.02)  # [m]
        self.rotation_range = config.get('rotation_range', [-20 * m.pi / 180, 30 * m.pi / 180])  # [rad]
        self.rotation_sensibility = config.get('rotation_sensibility', 10 * m.pi / 180)  # [rad]
        self.axis_position = config.get('axis_position', 2)  # z
        self.axis_rotation = config.get('axis_rotation', 1)  # pitch Euler angles
        self._position_is_terminal = False
        self._rotation_is_terminal = False

    def reward(self):
        position, rotation_quaternion = p.getBasePositionAndOrientation(self.uid)
        position_axis = position[self.axis_position]
        rotation_euler_axis = p.getEulerFromQuaternion(rotation_quaternion)[self.axis_rotation]
        self._position_is_terminal = position_axis < self.position_limit
        position_reward = self.multiplier_position * normalize(position_axis, self.position_limit, self.position_limit + self.position_sensibility)
        self._rotation_is_terminal = rotation_euler_axis < self.rotation_range[0] or self.rotation_range[1] < rotation_euler_axis
        rotation_reward = self.multiplier_rotation \
            * normalize(rotation_euler_axis, self.rotation_range[0], self.rotation_range[0] + self.rotation_sensibility) \
            * normalize(rotation_euler_axis, self.rotation_range[1], self.rotation_range[1] - self.rotation_sensibility)

        terminal_penality = self.terminal_penality if self.is_terminal() else 0

        return 0.5 * (position_reward + rotation_reward) - terminal_penality

    def is_terminal(self):
        return self._position_is_terminal or self._rotation_is_terminal  # terminal is any

    def reset(self):
        self._position_is_terminal = False
        self._rotation_is_terminal = False
        p.resetBasePositionAndOrientation(self.uid, *self.initial_pose)


class ExtendedObjectStateSensor(ObjectStateSensor):
    """Add acceleration sensing
    
    Known issue: measures acceleration on complete robot, not only one object
    """
    def __init__(self, parent, config):
        self.include_acceleration = config.get('include_acceleration', False)
        if self.include_acceleration:
            config.set('include_velocity', True)

        super(ExtendedObjectStateSensor, self).__init__(parent, config)

        if self.include_acceleration:
            self.observation_space.spaces['acceleration'] = spaces.Box(-10, 10, shape=(3, ), dtype='float32')

        self.dt = config.get('timestamp', 1/240.)
        self._previous_velocity = None

    def reset(self):
        self._previous_velocity = None

    def observe(self):
        obs = super(ExtendedObjectStateSensor, self).observe()
        if self._previous_velocity is None:
            obs['acceleration'] = np.array([0., 0., 0.], dtype='float32')
        else:
            obs['acceleration'] = (obs['velocity'] - self._previous_velocity) / self.dt
        self._previous_velocity = obs['velocity']
        return obs


AddonFactory.register_addon('velocity_reward', VelocityReward)
AddonFactory.register_addon('poise_reward', PoiseReward)
AddonFactory.register_addon('extended_object_state_sensor', ExtendedObjectStateSensor)


class WalbiObservationRestriction(gym.ObservationWrapper):
    """
    {'robot': {
        'joint_state': {
            'position': [-0.09982632881081135,
                        -0.5000089843741404,
                        1.0000387954528964,
                        -0.49873683516780304,
                        0.10091867299871378,
                        0.0999610583858461,
                        -0.5000022173009758,
                        1.0000831683667313,
                        -0.4987861018712393,
                        -0.10098325459397588],
            'velocity': [2.5248969990478506e-05,
                        7.663200426963354e-06,
                        4.105426139509241e-06,
                        4.440746957801192e-06,
                        0.00015239702286515597,
                        -6.689686926633536e-06,
                        -2.0698496901681806e-06,
                        -3.7708466390804803e-06,
                        2.023705072632351e-05,
                        -0.00016632607762649974]}),
        'pose': {'acceleration': array([ 2.36463499e-05,  3.13147509e-04, -1.05081705e-05]),
                'angular_velocity': array([1.78637576e-04, 1.10377248e-05, 2.51416412e-04]),
                'position': array([-3.34891700e-04, -1.94224801e-04,  2.76028229e-01]),
                'rotation': (0.00011995706100123976,
                            -0.0011488877034330981,
                            0.0016526058755881698),
                'velocity': array([-5.95733178e-05, -1.85549519e-04,  5.42000523e-06])},
        'weight_module_left': {'force': (-1.0500355387235578,
                                        2.1061296698973373,
                                        -8.61719779979664),
                                'torque': (0.0,
                                        0.032218887798794296,
                                        -0.07979533520428816)},
        'weight_module_right': {'force': (1.054494933578446,
                                        -2.104885898314442,
                                        -7.8183147653093785),
                                'torque': (-1.2924697071141057e-26,
                                            0.054716556197296,
                                            0.005379510114275714)}}
    """

    def __init__(self, env):
        super().__init__(env)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(28,))  # low high innacurate
        self.action_space = gym.spaces.Box(
            low=np.array([-0.5, -1, -0.2, -0.9, -0.5, -0.2, -1, -0.2, -0.9, -0.5]),
            high=np.array([0.2, 1, 2.0, 0.7, 0.5, 0.5, 1, 2.0, 0.7, 0.5])
        )
        self._max_episode_steps = 50000

    def observation(self, observation):
        joint_positions = self._reduce_precision_int16(observation['robot']['joint_state']['position'], 512 / m.pi)
        joint_rate = observation['robot']['joint_state']['velocity']
        weight_left = self._reduce_precision_int16(-0.1 * observation['robot']['weight_module_left']['force'][2], 400)
        weight_right = self._reduce_precision_int16(-0.1 * observation['robot']['weight_module_right']['force'][2], 400)
        accelerometer = self._reduce_precision_int16(observation['robot']['pose']['acceleration'], 1000)
        gyrometer = self._reduce_precision_int16(observation['robot']['pose']['angular_velocity'], 100)

        scaling = np.array(10 * [1] + 10 * [10] + [1, 1] + [1, 1, 1, 10, 10, 10], dtype='float32')
        return scaling * np.array(joint_positions + joint_rate + [weight_left, weight_right] + accelerometer + gyrometer, dtype='float32')

    def _reduce_precision_int16(self, value, float_to_int_factor):
        """Represents how a physical value is encoded as an int16 on the Arduino, transmitted,
        then converted to a float"""
        if isinstance(value, (list, tuple, np.ndarray)):
            return [self._reduce_precision_int16(v, float_to_int_factor) for v in value]
        else:
            if float_to_int_factor:
                return max(-32768, min(32767, int(value * float_to_int_factor))) / float_to_int_factor
            else:
                return 0


def make_env():
    # should use absolute path in yaml config file to avoid URDF files copy
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'walbi.yaml')
    env = WalbiObservationRestriction(DIYGym(config_file))
    return env


if __name__ == '__main__':
    from itertools import count
    import time
    from inverse_kinematic import Walker

    env = make_env()
    dt = 1/240.
    walker = Walker()

    observation = env.reset()
    for i in count(0):
        t = i * dt
        action = walker.walk(t)
        observation, reward, terminal, info = env.step(action)

        #if terminal:
        #    env.reset()
