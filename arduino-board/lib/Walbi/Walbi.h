#ifndef WALBI_H
#define WALBI_H

#include <Arduino.h>

#include <Stream.h>

#include "ServoBus.h"
#include "robust_serial.h"

namespace walbi_ns
{

#define PROTOCOL_VERSION 3

const long DEBUG_BOARD_BAUD = 115200;  // Baudrate to DebugBoard
const uint8_t MOTOR_NB = 10;
const uint8_t MOTOR_IDS[MOTOR_NB] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

// Define the messages that can be sent and received
enum Message {
    OK = 1,  // acknowledge reception
    CONNECT = 2,
    ALREADY_CONNECTED = 3,
    RESET = 4,
    STEP = 5,
    ACTION = 6,
    STATE = 7,
    CLOSE = 8,
    INFO = 9,
    ERROR = 10,
    VERSION = 11,
};
typedef enum Message Message;
Message read_message();
void write_message(enum Message myMessage);

enum ErrorCode {
    RECEIVED_UNKNOWN_MESSAGE = 0,
    EXPECTED_OK = 1,
    EXPECTED_ACTION = 2,
    DID_NOT_EXPECT_OK = 3,
    NOT_IMPLEMENTED_YET = 4,
};

struct State
{
    unsigned long timestamp;
    uint16_t positions[MOTOR_NB];
};

struct Action
{
    uint16_t commands[MOTOR_NB][2];
};

class Walbi
{
private:
    ServoBus* servoBus_;
    State* readPositionsFromDebugBoard_();
	static void receivePositionFromDebugBoard_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2);
    State* refreshStateIfNeeded_();

    unsigned long intervalReadSerial_; // interval at which to handle messages
	unsigned long intervalRefreshState_; // interval at which to get state
public:
    uint8_t motorIds[MOTOR_NB];
    bool isConnected = false;
    bool connect(); // run this in setup

    Walbi(uint8_t debugBoardRx, uint8_t debugBoardTx, long computerSerialBaud, unsigned long intervalReadSerial = 0, unsigned long intervalRefreshState = 0, bool autoConnect = true);
    Walbi(Stream* debugBoardStream, long computerSerialBaud, unsigned long intervalReadSerial = 0, unsigned long intervalRefreshState = 0, bool autoConnect = true);

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
