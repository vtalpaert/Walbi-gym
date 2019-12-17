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

#define PROTOCOL_VERSION 6

const long DEBUG_BOARD_BAUD = 115200;  // Baudrate to DebugBoard
const uint8_t MOTOR_NB = 10;
const uint8_t MOTOR_IDS[MOTOR_NB] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}; // IDs different than [0:9] is not supported

// Define the messages that can be sent and received
enum Message {
    OK = 1, // acknowledges reception
    NOK = 2, // asks for resend
    CONNECT = 3,
    ALREADY_CONNECTED = 4,
    RESET = 5,
    STEP = 6,
    ACTION = 7,
    STATE = 8,
    CLOSE = 9,
    INFO = 10,
    ERROR = 11,
    VERSION = 12,
};
typedef enum Message Message;
Message read_message();
void write_message(enum Message myMessage);

enum ErrorCode {
    RECEIVED_UNKNOWN_MESSAGE = 0,
    EXPECTED_OK = 1,
    DID_NOT_EXPECT_OK = 2,
    DID_NOT_EXPECT_NOK = 3,
    DID_NOT_EXPECT_MESSAGE = 4,
    NOT_IMPLEMENTED_YET = 5,
    SENSOR_ERROR_WEIGHT = 6,
    SENSOR_ERROR_IMU = 7,
};

struct State
{ // can only be int types
    unsigned long timestamp;
    uint16_t positions[MOTOR_NB];
    bool is_position_updated[MOTOR_NB];
    bool correct_motor_reading;
    long weight_left;
    long weight_right;
};

struct Action
{ // can only be int types
    uint16_t commands[MOTOR_NB][3]; // [position, span, activate]
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

    unsigned long intervalReadSerial_; // interval at which to handle messages
	unsigned long intervalRefreshState_; // interval at which to get state
public:
    IMU imu;

    uint8_t motorIds[MOTOR_NB];
    bool isConnected = false;
    bool connect(); // run this in setup

    Walbi(Stream* debugBoardStream, uint8_t imu_address = DEFAULT_IMU_ADDRESS, unsigned long intervalReadSerial = 0, unsigned long intervalRefreshState = 0);
    void begin(long computerSerialBaud, unsigned char dout_left, unsigned char dout_right, unsigned char pd_sck_left, unsigned char pd_sck_right, bool autoConnect = true, unsigned long delay_ready = 1000);

    // interact with hardware
    State* getState(); // collect from sensors
    void act(Action* action); // send to actuators

    // Serial communication
    bool handleMessagesFromSerial();
    bool receiveAction(Action* action);
    bool sendState(State* state);

    // run in loop
    void run();
};

} // namespace walbi_ns
#endif // WALBI_H
