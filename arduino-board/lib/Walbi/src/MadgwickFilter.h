#ifndef MADGWICKFILTER_H
#define MADGWICKFILTER_H

#include <Arduino.h>

class MadgwickFilter
{
private:
    float pi = 3.141592653589793238462643383279502884f;
    float GyroMeasError = pi * (40.0f / 180.0f);   // gyroscope measurement error in rads/s (start at 40 deg/s)
    float GyroMeasDrift = pi * (0.0f  / 180.0f);   // gyroscope measurement drift in rad/s/s (start at 0.0 deg/s/s)
    float beta = sqrtf(3.0f / 4.0f) * GyroMeasError;   // compute beta
    float zeta = sqrtf(3.0f / 4.0f) * GyroMeasDrift;   // compute zeta, the other free parameter in the Madgwick scheme usually set to a small or zero value
    float deltat = 0.0f, sum = 0.0f;          // integration interval for both filter schemes
    uint32_t lastUpdate = 0, firstUpdate = 0; // used to calculate integration interval
    uint32_t Now = 0;                         // used to calculate integration interval
    float a12, a22, a31, a32, a33;            // rotation matrix coefficients for Euler angles and gravity components
public:
    float q[4] = {1.0f, 0.0f, 0.0f, 0.0f};    // vector to hold quaternion
    float roll, pitch, yaw;                   // absolute orientation
    float   magBias[3] = {-23.15, 359.62, -463.05}, magScale[3]  = {1.00, 1.02, 0.98}; // Bias corrections for gyro and accelerometer
    void MadgwickQuaternionUpdate(float ax, float ay, float az, float gx, float gy, float gz, float mx, float my, float mz);
    void EulerAnglesCalculation(float yaw_correction);
};

#endif // MADGWICKFILTER_H