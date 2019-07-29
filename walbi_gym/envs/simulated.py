from walbi_gym.envs.utils import _clip

class LX16A(object):
    """Motor class with instant max speed towards target position"""

    resolution = 0.24  # [deg]
    max_speed = 1550  # [tick/s] supposedly 62 RPM, so 62 / 60 * 360 / 0.24
    time_to_reach_max_speed = 0.5  # [s] limits acceleration
    min_position_encoder = 0
    max_position_encoder = 1023

    def __init__(self, initial_position=512):
        self.position_encoder = initial_position
        self.speed = 0

    def step(self, dt, target_encoder):
        if target_encoder > self.position_encoder:
            direction = +1
        elif target_encoder < self.position_encoder:
            direction = -1
        else:  # equal case
            direction = 0
        if self.time_to_reach_max_speed == 0:
            self.speed = direction * self.max_speed
        else:
            self.speed = _clip(self.speed + direction * dt / self.time_to_reach_max_speed, - self.max_speed, self.max_speed)
        self.position_encoder = _clip(self.position_encoder +  dt * self.speed, self.min_position_encoder, self.max_position_encoder)
        return self.position_encoder
