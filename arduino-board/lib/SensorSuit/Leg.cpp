#include "Leg.h"

//Build the instance of Leg
//Defines the analog inputs of the Arduino for the leg.
void Leg::build(int s, int p_a_x, int p_a_y, int p_a_z, int p_k, int p_h_x, int p_h_y, int p_h_z, int o_a_x, int o_a_y, int o_a_z, int o_k, int o_h_x, int o_h_y, int o_h_z)
{
    side = s;

    pin_ankle_x = p_a_x;
    pin_ankle_y = p_a_y;
    pin_ankle_z = p_a_z;
    pin_knee = p_k;
    pin_hip_x = p_a_x;
    pin_hip_y = p_a_y;
    pin_hip_z = p_a_z;

    pinMode(pin_ankle_x, INPUT);
    pinMode(pin_ankle_y, INPUT);
    pinMode(pin_ankle_z, INPUT);
    pinMode(pin_knee, INPUT);
    pinMode(pin_hip_x, INPUT);
    pinMode(pin_hip_y, INPUT);
    pinMode(pin_hip_z, INPUT);

    offset_ankle_x = o_a_x;
    offset_ankle_y = o_a_y;
    offset_ankle_z = o_a_z;
    offset_knee = o_k;
    offset_hip_x = o_a_x;
    offset_hip_y = o_a_y;
    offset_hip_z = o_a_z;
}

//Get the leg joints' position (raw values)
void Leg::getValues()
{
    for (int i = 0; i < joint_number; i++)
    {
        value_table[i] = analogRead(pin_table[i]) - 512;
    }
}

//Get the leg joints' position (angles)
void Leg::getAngles()
{
    getValues();
    for (int i = 0; i < joint_number; i++)
    {
        value_table[i] *= 135 / 512;
        value_table[i] -= offset_table[i];
    }
}

//Update the leg joints' offsets
void Leg::updateOffsets(int o_a_x, int o_a_y, int o_a_z, int o_k, int o_h_x, int o_h_y, int o_h_z)
{
    offset_ankle_x = o_a_x;
    offset_ankle_y = o_a_y;
    offset_ankle_z = o_a_z;
    offset_knee = o_k;
    offset_hip_x = o_h_x;
    offset_hip_y = o_h_y;
    offset_hip_z = o_h_z;
}