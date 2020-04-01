import math as m
import numpy as np


class JointsAngleCalculator(object):

    """Calculates joints angle specifically for Walbi robot
    
    Assumptions:
        The feet are always level with the hips
        We only need to control three joints per feet to position the heel in space
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
