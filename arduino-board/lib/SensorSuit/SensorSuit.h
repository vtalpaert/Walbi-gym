#ifndef SensorSuit_h
#define SensorSuit_h

#include "Arduino.h"
#include "Leg.h"


class SensorSuit
{
public:
    void build(Leg right_leg, Leg left_leg);
    void getValues();
    void getAngles();
    void sendValues();

    Leg r_leg;
    Leg l_leg;

};

#endif