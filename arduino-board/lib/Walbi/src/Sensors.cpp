#include "Sensors.h"

#include "Wire.h" // I2C library

IMU::IMU(uint8_t address)
{
    this->mpu_ = new MPU9250(Wire, address);
};

int IMU::begin()
{
    this->status = this->mpu_->begin();
    if (this->status < 0)
    {
    return this->status;
    }
    // setting the accelerometer full scale range to +/-8G 
    this->mpu_->setAccelRange(MPU9250::ACCEL_RANGE_8G);
    // setting the gyroscope full scale range to +/-500 deg/s
    this->mpu_->setGyroRange(MPU9250::GYRO_RANGE_500DPS);
    // setting DLPF bandwidth to 20 Hz
    this->mpu_->setDlpfBandwidth(MPU9250::DLPF_BANDWIDTH_20HZ);
    // setting SRD to 19 for a 50 Hz update rate
    this->mpu_->setSrd(19);

    this->mpu_->setMagCalX(-4.970144, 1.126202);
    this->mpu_->setMagCalY(30.307353, 0.960394);
    this->mpu_->setMagCalZ(-32.890918, 0.933863);

    return this->status;
};


void IMU::calibrateMag(){
    Serial.println("Start mag cal");
    this->status = this->mpu_->calibrateMag();
    if (status < 0) {
        Serial.println("Mag calibration unsuccessful");
        Serial.print("Status: ");
        Serial.println(this->status);
        while(1) {}
    }
    Serial.print("BiasX: ");
    Serial.println(this->mpu_->getMagBiasX_uT(), 6);
    Serial.print("ScaleX: ");
    Serial.println(this->mpu_->getMagScaleFactorX(), 6);

    Serial.print("BiasY: ");
    Serial.println(this->mpu_->getMagBiasY_uT(), 6);
    Serial.print("ScaleY: ");
    Serial.println(this->mpu_->getMagScaleFactorY(), 6);

    Serial.print("BiasZ: ");
    Serial.println(this->mpu_->getMagBiasZ_uT(), 6);
    Serial.print("ScaleZ: ");
    Serial.println(this->mpu_->getMagScaleFactorZ(), 6);

    delay(200000); // add delay to see results before serial spew of data
};


void IMU::update()
{
    // read the sensor
    this->mpu_->readSensor();

    ax = this->mpu_->getAccelX_mss();
    ay = this->mpu_->getAccelY_mss();
    az = this->mpu_->getAccelZ_mss();
    gx = this->mpu_->getGyroX_rads();
    gy = this->mpu_->getGyroY_rads();
    gz = this->mpu_->getGyroZ_rads();
    mx = this->mpu_->getMagX_uT();
    my = this->mpu_->getMagY_uT();
    mz = this->mpu_->getMagZ_uT();

    //MadgwickQuaternionUpdate(-ax, ay, az, gx, -gy, -gz,  my,  -mx, mz);
    this->filter_.MadgwickQuaternionUpdate(ax, ay, az, gx, gy, gz,  my, mx, mz);
    this->filter_.EulerAnglesCalculation(this->yaw_correction);
    this->roll = this->filter_.roll;
    this->pitch = this->filter_.pitch;
    this->yaw = this->filter_.yaw;
};

int16_t IMU::convertAccel(float a)
{
    return (int16_t) a * 1000;
};

float IMU::convertAccel(int16_t a_raw)
{
    return (float) a_raw / 1000;
};

int16_t IMU::convertGyro(float g)
{
    return (int16_t) g * 10;
};

float IMU::convertGyro(int16_t g_raw)
{
    return (float) g_raw / 10;
};

int16_t IMU::convertAngleDeg(float angle)
{
    if (angle > 180)
    {
        angle -= 180;
    }
    return (int16_t) angle * 1000;
};

float IMU::convertAngleDeg(int16_t angle_raw)
{
    return (float) angle_raw / 1000;
};
