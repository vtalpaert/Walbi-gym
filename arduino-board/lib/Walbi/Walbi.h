#ifndef WALBI_H
#define WALBI_H

#include <Arduino.h>
#include <SoftwareSerial.h>

#include "../ServoBus/ServoBus.h"
#include "../robust_serial/robust_serial.h"

namespace Walbi
{

#define SOFTWARE_SERIAL_BAUD 115200  // Baudrate to DebugBoard
#define MOTOR_NB 10
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
    CONFIG = 10,
    ERROR = 11,
};
typedef enum Message Message;
Message read_message();
void write_message(enum Message myMessage);

class Walbi
{
private:
    SoftwareSerial* mySerial_;
    ServoBus* bus_;
public:
    uint16_t positions[MOTOR_NB];
    uint8_t motor_ids[MOTOR_NB];
    bool is_connected = false;
    bool connect();  // run this in setup

    Walbi(uint8_t DEBUG_BOARD_RX, uint8_t DEBUG_BOARD_TX, uint8_t COMPUTER_SERIAL_BAUD, bool auto_connect=true);
    void read_positions();

    void get_messages_from_serial(); // run this in loop
    bool action();
    bool observation();
    bool reward();
    bool step();
    bool reset();
};

} // namespace
#endif
