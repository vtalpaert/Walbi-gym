#ifndef Leg_h
#define Leg_h

#include "Arduino.h"

#define LEFT = 1;
#define RIGHT = 0;

class Leg
{
public:
    void build(int s, int p_a_x, int p_a_y, int p_a_z, int p_k, int p_h_x, int p_h_y, int p_h_z, int o_a_x = 0, int o_a_y = 0, int o_a_z = 0, int o_k = 0, int o_h_x = 0, int o_h_y = 0, int o_h_z = 0);
    void getValues();
    void getAngles();
    void updateOffsets(int o_a_x, int o_a_y, int o_a_z, int o_k, int o_h_x, int o_h_y, int o_h_z);

    static const int joint_number = 7;

    int side; // 0 = right side, 1 = left side.

    int pin_ankle_x;
    int pin_ankle_y;
    int pin_ankle_z;
    int pin_knee;
    int pin_hip_x;
    int pin_hip_y;
    int pin_hip_z;
    int pin_table[joint_number] = {pin_ankle_x, pin_ankle_y, pin_ankle_z, pin_knee, pin_hip_x, pin_hip_y, pin_hip_z};

    int ankle_x;
    int ankle_y;
    int ankle_z;
    int knee;
    int hip_x;
    int hip_y;
    int hip_z;
    int value_table[joint_number] = {ankle_x, ankle_y, ankle_z, knee, hip_x, hip_y, hip_z};

    int offset_ankle_x = 0;
    int offset_ankle_y = 0;
    int offset_ankle_z = 0;
    int offset_knee = 0;
    int offset_hip_x = 0;
    int offset_hip_y = 0;
    int offset_hip_z = 0;
    int offset_table[joint_number] = {offset_ankle_x, offset_ankle_y, offset_ankle_z, offset_knee, offset_hip_x, offset_hip_y, offset_hip_z};
};

#endif
