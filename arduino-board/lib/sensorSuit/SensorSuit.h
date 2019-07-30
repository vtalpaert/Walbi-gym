#ifndef SensorSuit_h
#define SensorSuit_h

#include "Arduino.h"
#include "Leg.h"


class SensorSuit
{
public:
    void SensorSuit::build(Leg right_leg, Leg left_leg);
    void SensorSuit::getValues();
    void SensorSuit::getAngles();
    void SensorSuit::sendValues();

    Leg r_leg;
    Leg l_leg;

};

#endif