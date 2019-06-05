#ifndef WALBI_H
#define WALBI_H

#include <Arduino.h>
#include <SoftwareSerial.h>

#include "../ServoBus/ServoBus.h"
#include "../robust_serial/robust_serial.h"

namespace Walbi
{

#define VERSION 1.0

const long SOFTWARE_SERIAL_BAUD = 115200;  // Baudrate to DebugBoard
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
    OBSERVATION = 7,
    REWARD = 8,  // send two values; reward and termination
    CLOSE = 9,
    INFO = 10,
    ERROR = 11,
    TIMESTAMP_OBSERVATION = 12,
};
typedef enum Message Message;
Message read_message();
void write_message(enum Message myMessage);

enum ErrorCode {
    RECEIVED_UNKNOWN_MESSAGE = 0,
    EXPECTED_ACTION = 1,
    EXPECTED_OK = 2,
    DID_NOT_EXPECT_OK = 3,
    NOT_IMPLEMENTED_MESSAGE = 4,
};

class Walbi
{
private:
    SoftwareSerial* mySerial_;
    ServoBus* bus_;
    int16_t timestamp_delta_highest_allowed_ = 10000; // when difference between two ts is too high, signal timeout
    int16_t timestamp_delta_timeout_signal_ = -10000; // will become -1 when scaled
public:
    uint16_t positions[MOTOR_NB];
    uint8_t motor_ids[MOTOR_NB];
    bool is_connected = false;
    bool connect();  // run this in setup

    Walbi(uint8_t DEBUG_BOARD_RX, uint8_t DEBUG_BOARD_TX, long COMPUTER_SERIAL_BAUD, bool auto_connect=true);
    void read_positions();
    void get_messages_from_serial();
    void collect_observation();

    void run_once(); // run this in loop
    bool action();
    bool observation();
    bool reward();
    bool step();
    bool reset();
};

} // namespace
#endif
