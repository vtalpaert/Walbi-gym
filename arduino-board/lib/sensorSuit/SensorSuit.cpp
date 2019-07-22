#include "SensorSuit.h"

void SensorSuit::build(Leg right_leg, Leg left_leg)
{
    r_leg = right_leg;
    l_leg = left_leg;
}

void SensorSuit::getValues()
{
    r_leg.getValues();
    l_leg.getValues();
}

void SensorSuit::getAngles()
{
    r_leg.getAngles();
    l_leg.getAngles();
}