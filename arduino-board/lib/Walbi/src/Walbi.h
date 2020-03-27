#ifndef WALBI_H
#define WALBI_H

#include <Arduino.h>
#include <Stream.h>

// librarie files
#include "Sensors.h"

// external libraries
#include "ServoBus.h"
#include "robust_serial.h"
#include "HX711.h"

namespace walbi_ns
{

#define PROTOCOL_VERSION 8

const long DEBUG_BOARD_BAUD = 115200;  // Baudrate to DebugBoard
const uint8_t MOTOR_NB = 10;
const uint8_t MOTOR_IDS[MOTOR_NB] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}; // IDs different than [0..9] is not supported

// Define the messages that can be sent and received
enum Message {
    OK = 1, // acknowledges reception
    CONNECT = 2,
    ALREADY_CONNECTED = 3,
    ERROR = 4,
    VERSION = 5,
    SET = 6,
    ACTION = 7,
    STATE = 8,
};
typedef enum Message Message;
Message read_message();
void write_message(enum Message myMessage);

enum ErrorCode {
    RECEIVED_UNKNOWN_MESSAGE = 0,
    EXPECTED_OK = 1,
    DID_NOT_EXPECT_OK = 2,
    DID_NOT_EXPECT_MESSAGE = 3,
    NOT_IMPLEMENTED_YET = 4,
    SENSOR_ERROR_WEIGHT = 5,
    SENSOR_ERROR_IMU = 6,
    INCOMPLETE_MESSAGE = 7,
};

struct State
{ // can only be int types
    unsigned long timestamp;
    uint16_t position[MOTOR_NB];
    bool is_position_updated[MOTOR_NB];
    bool correct_motor_reading;
    long weight_left;
    long weight_right;
    int16_t imu[9]; // [ax, ay, az, gx, gy, gz, roll, pitch, yaw]
};

struct Action
{ // can only be int types
    uint16_t position[MOTOR_NB];
    uint16_t span[MOTOR_NB];
    bool activate[MOTOR_NB]; // [position, span, activate]
};

class Walbi
{
private:
    HX711 weight_sensor_left_;
    HX711 weight_sensor_right_;

    ServoBus* servoBus_;
    State* readPositionsFromDebugBoard_();
	static void receivePositionFromDebugBoard_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2);
    State* refreshStateIfNeeded_();
    bool sendStateIfNeeded_(State* state);

    unsigned long intervalReadSerial_; // interval at which to handle messages
	unsigned long intervalRefreshState_; // interval at which to get state
    unsigned long intervalSendState_; // interval at which to send state
public:
    IMU imu;

    uint8_t motorIds[MOTOR_NB];
    bool isConnected = false;
    bool connect(); // run this in setup

    Walbi(Stream* debugBoardStream, uint8_t imu_address = DEFAULT_IMU_ADDRESS, unsigned long intervalReadSerial = 0, unsigned long intervalRefreshState = 0, unsigned long intervalSendState = 0);
    void begin(long computerSerialBaud, unsigned char dout_left, unsigned char dout_right, unsigned char pd_sck_left, unsigned char pd_sck_right, bool autoConnect = true, unsigned long delay_ready = 1000);

    // interact with hardware
    State* getState(); // collect from sensors
    void act(Action* action); // send to actuators

    // Serial communication
    bool handleMessagesFromSerial();
    bool receiveAction(Action* action);
    bool sendState(State* state);

    // run in loop
    void run(bool autoSendState = false);
};

} // namespace walbi_ns
#endif // WALBI_H
