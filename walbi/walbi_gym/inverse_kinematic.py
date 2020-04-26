import math as m
import numpy as np


class Walker(object):

    """Calculates joints angle specifically for Walbi robot
    
    Assumptions:
        The feet are always level with the hips, so two joints are deduced from the hip position
        We only need to control three joints per foot to position the heel in space
        We simplify the math by assuming the hip joints are at distance 0.
        The coordinates x, y, z are for the feet with respect to the hip joint, so z is always negative
        Output is RHX, RHY, RK, RFY, RFX, LHY, LHX, LK, LFX, LFY
    
    """
    def __init__(self):
        pass

    def calculate_joints_angle(self, x, y, z):
        # right foot
        l_upper = 0.11
        l_lower = 0.11
        x = -x
        z = max(0.05, min(-z, l_upper + l_lower))
        RHX = m.atan(y/z)
        z3 = z/m.cos(RHX)
        RHY2 = m.atan(x/z3)
        z2 = z3/m.cos(RHY2)
        RHY = -m.acos((z2**2+l_upper**2-l_lower**2)/(2.*l_upper*z2)) + RHY2
        RK = m.pi - m.acos((l_upper**2+l_lower**2-z2**2)/(2.*l_upper*l_lower))
        RFY = -RHY-RK
        return np.array([RHX, RHY, RK, RFY, -RHX])

    def circlesXZ(self, t, freq = 0.05):
        x = 0. + 0.03 * m.sin(2*m.pi*freq*t)
        y = -0.05
        z = -0.15 + 0.04 * m.cos(2*m.pi*freq*t)
        action = np.empty(10, dtype=float)
        action[:5] = calculator.calculate_joints_angle(x, y, z)  # right
        action[5:] = calculator.calculate_joints_angle(x, -y, z)  # left
        return action

    def tiptapsYZ(self, t, freq = 0.1):
        x = 0
        y = 0.04 * m.sin(2*m.pi*freq*t)
        z = -0.17
        z_up_right = max(0, 0.07 * m.sin(2*m.pi*freq*t + m.pi) - 0.05)
        z_up_left = max(0, 0.07 * m.sin(2*m.pi*freq*t) - 0.05)
        action = np.empty(10, dtype=float)
        action[:5] = calculator.calculate_joints_angle(x, y, z + z_up_right)  # right
        action[5:] = calculator.calculate_joints_angle(x, y, z + z_up_left)  # left
        return action

    def walk_one_period(self, p, delta_x):
        amplitude_y = 0.05
        amplitude_z = 0.03
        z = -0.17  # base height

        y = amplitude_y * m.sin(2*m.pi*p)
        z_up_left = 0
        z_up_right = 0
        rate = -2. / 0.9
        if p <= 0.2:
            x_left = delta_x * (-1 + rate * (p - 0.2))
            x_right = delta_x * (-1 + rate * (p - 0.7))
        elif 0.2 < p < 0.3:  # left up
            z_up_left = amplitude_z * 0.5 * (1 - m.cos(2*m.pi*(p-0.2)/(0.1)))
            x_left = - delta_x * m.cos(m.pi*(p-0.2)/(0.1))
            x_right = delta_x * (-1 + rate * (p - 0.7))
        elif 0.3 <= p <= 0.7:
            x_left = delta_x * (1 + rate * (p - 0.3))
            x_right = delta_x * (-1 + rate * (p - 0.7))
        elif 0.7 < p < 0.8:  # right up
            z_up_right = amplitude_z * 0.5 * (1 - m.cos(2*m.pi*(p-0.7)/(0.1)))
            x_left = delta_x * (1 + rate * (p - 0.3))
            x_right = - delta_x * m.cos(m.pi*(p-0.7)/(0.1))
        else:
            x_left = delta_x * (1 + rate * (p - 0.3))
            x_right = delta_x * (1 + rate * (p - 0.8))
        action = np.empty(10, dtype=float)
        action[:5] = self.calculate_joints_angle(x_right, y, z + z_up_right)  # right
        action[5:] = self.calculate_joints_angle(x_left, y, z + z_up_left)  # left
        return action

    def walk(self, t, freq = 0.5, delta_x = 0.07):
        p = (freq*t) % 1
        return self.walk_one_period(p, delta_x)
