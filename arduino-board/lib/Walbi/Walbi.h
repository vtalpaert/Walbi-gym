#ifndef WALBI_H
#define WALBI_H

#include <Arduino.h>
#include <SoftwareSerial.h>

#include "../ServoBus/ServoBus.h"
#include "../robust_serial/robust_serial.h"

namespace Walbi
{

#define PROTOCOL_VERSION 2

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
    int16_t reward;
    int8_t done;
};

struct Action
{
    uint16_t commands[MOTOR_NB][2];
};

class Walbi
{
private:
    SoftwareSerial* mySerial_;
    ServoBus* bus_;
    State* read_positions_from_debug_board_();
	static void receive_position_from_debug_board_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2);
    State* refresh_state_if_needed_();

    unsigned long interval_read_serial_; // interval at which to handle messages
	unsigned long interval_refresh_state_; // interval at which to get state
public:
    uint8_t motor_ids[MOTOR_NB];
    bool is_connected = false;
    bool connect(); // run this in setup

    Walbi(uint8_t debug_board_rx, uint8_t debug_board_tx, long computer_serial_baud, unsigned long interval_read_serial = 0, unsigned long interval_refresh_state = 0, bool auto_connect=true);

    // interact with hardware
    State* get_state(); // collect from sensors
    void act(Action* action); // send to actuators

    // Serial communication
    bool handle_messages_from_serial();
    bool receive_action(Action* action, bool listen_for_message);
    bool send_state(State* state);

    // run in loop
    void run();
};

} // namespace
#endif
