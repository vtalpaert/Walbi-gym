#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

// external libraries
#include "MPU9250.h"
#include "MadgwickFilter.h"

const uint8_t DEFAULT_IMU_ADDRESS=0x68;

class IMU
{
private:
    MPU9250* mpu_; // MPU-9250 sensor on I2C bus 0 with default address of 0x68
    MadgwickFilter filter_;
public:
    int status;
    float yaw_correction=0.36; // Paris on 2019-12-12

    float ax, ay, az, gx, gy, gz, mx, my, mz; // variables to hold latest sensor data values
    float roll, pitch, yaw;                   // absolute orientation

    IMU(uint8_t address);
    int begin();
    void update();
    void calibrateMag(); // prints to Serial, beware it has .begin()
}; // end IMU

#endif // SENSORS_H