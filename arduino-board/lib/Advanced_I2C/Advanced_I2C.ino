#include "MPU9250.h"

float pi = 3.141592653589793238462643383279502884f;
float GyroMeasError = pi * (40.0f / 180.0f);   // gyroscope measurement error in rads/s (start at 40 deg/s)
float GyroMeasDrift = pi * (0.0f  / 180.0f);   // gyroscope measurement drift in rad/s/s (start at 0.0 deg/s/s)
float beta = sqrtf(3.0f / 4.0f) * GyroMeasError;   // compute beta
float zeta = sqrtf(3.0f / 4.0f) * GyroMeasDrift;   // compute zeta, the other free parameter in the Madgwick scheme usually set to a small or zero value
float deltat = 0.0f, sum = 0.0f;          // integration interval for both filter schemes
uint32_t lastUpdate = 0, firstUpdate = 0; // used to calculate integration interval
uint32_t Now = 0;                         // used to calculate integration interval
float ax, ay, az, gx, gy, gz, mx, my, mz; // variables to hold latest sensor data values 
float q[4] = {1.0f, 0.0f, 0.0f, 0.0f};    // vector to hold quaternion
float pitch, yaw, roll;                   // absolute orientation
float a12, a22, a31, a32, a33;            // rotation matrix coefficients for Euler angles and gravity components
float   magBias[3] = {-23.15, 359.62, -463.05}, magScale[3]  = {1.00, 1.02, 0.98}; // Bias corrections for gyro and accelerometer

// an MPU9250 object with the MPU-9250 sensor on I2C bus 0 with address 0x68
MPU9250 IMU(Wire,0x68);
int status;

void calibMag(){
  Serial.println("Start mag cal");
  status = IMU.calibrateMag();
  if (status < 0) {
    Serial.println("Mag calibration unsuccessful");
    Serial.print("Status: ");
    Serial.println(status);
    while(1) {}
  }
  Serial.print("BiasX: ");
  Serial.println(IMU.getMagBiasX_uT(), 6);
  Serial.print("ScaleX: ");
  Serial.println(IMU.getMagScaleFactorX(), 6);
  
  Serial.print("BiasY: ");
  Serial.println(IMU.getMagBiasY_uT(), 6);
  Serial.print("ScaleY: ");
  Serial.println(IMU.getMagScaleFactorY(), 6);

  Serial.print("BiasZ: ");
  Serial.println(IMU.getMagBiasZ_uT(), 6);
  Serial.print("ScaleZ: ");
  Serial.println(IMU.getMagScaleFactorZ(), 6);

  delay(200000); // add delay to see results before serial spew of data
}


void setup() {
  // serial to display data
  Serial.begin(115200);
  while(!Serial) {}

  // start communication with IMU 
  status = IMU.begin();
  if (status < 0) {
    Serial.println("IMU initialization unsuccessful");
    Serial.println("Check IMU wiring or try cycling power");
    Serial.print("Status: ");
    Serial.println(status);
    while(1) {}
  }
  // setting the accelerometer full scale range to +/-8G 
  IMU.setAccelRange(MPU9250::ACCEL_RANGE_8G);
  // setting the gyroscope full scale range to +/-500 deg/s
  IMU.setGyroRange(MPU9250::GYRO_RANGE_500DPS);
  // setting DLPF bandwidth to 20 Hz
  IMU.setDlpfBandwidth(MPU9250::DLPF_BANDWIDTH_20HZ);
  // setting SRD to 19 for a 50 Hz update rate
  IMU.setSrd(19);

  IMU.setMagCalX(-4.970144, 1.126202);
  IMU.setMagCalY(30.307353, 0.960394);
  IMU.setMagCalZ(-32.890918, 0.933863);
}

void loop() {
  // read the sensor
  IMU.readSensor();

  ax = IMU.getAccelX_mss();
  ay = IMU.getAccelY_mss();
  az = IMU.getAccelZ_mss();
  gx = IMU.getGyroX_rads();
  gy = IMU.getGyroY_rads();
  gz = IMU.getGyroZ_rads();
  mx = IMU.getMagX_uT();
  my = IMU.getMagY_uT();
  mz = IMU.getMagZ_uT();

  Now = micros();
  deltat = ((Now - lastUpdate)/1000000.0f); // set integration time by time elapsed since last filter update
  lastUpdate = Now;
  //MadgwickQuaternionUpdate(-ax, ay, az, gx, -gy, -gz,  my,  -mx, mz);
  MadgwickQuaternionUpdate(ax, ay, az, gx, gy, gz,  my, mx, mz);

  a12 =   2.0f * (q[1] * q[2] + q[0] * q[3]);
  a22 =   q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3];
  a31 =   2.0f * (q[0] * q[1] + q[2] * q[3]);
  a32 =   2.0f * (q[1] * q[3] - q[0] * q[2]);
  a33 =   q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3];
  pitch = -asinf(a32);
  roll  = atan2f(a31, a33);
  yaw   = atan2f(a12, a22);
  pitch *= 180.0f / pi;
  yaw   *= 180.0f / pi;
  yaw += 0.36; // Paris on 2019-12-12
  //if(yaw < 0) yaw   += 360.0f; // Ensure yaw stays between 0 and 360
  roll  *= 180.0f / pi;

  Serial.print(roll, 6); // +y
  Serial.print("\t");
  Serial.print(pitch, 6); // +x
  Serial.print("\t");
  //Serial.print(yaw, 6);
  Serial.println("");
  
  delay(20);
}
