#include "Walbi.h"

namespace Walbi
{

Message read_message() { return (Message) Serial.read(); }

void write_message(enum Message myMessage)
{
	uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

uint16_t last_received_position_;
unsigned long timestamp_successfully_sent_observation = 0;
unsigned long timestamp_gathered_observation = 0;
signed long delta = 0;

void receive_position_from_debug_board_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    (void)id;
    (void)command;
    (void)param2;
    last_received_position_ = param1;
}

void wait_for_serial() // blocking
{
    while (Serial.available() == 0) { delay(1); }
}

void Walbi::read_positions_from_debug_board_(State* state)
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        this->bus_->requestPosition(this->motor_ids[i]);
        state->positions[i] = last_received_position_;
    }
}

bool wait_acknowledge()
{
    wait_for_serial();
    Message message_received = read_message();
    if(message_received != OK)
    {
        write_message(ERROR);
        write_i8(EXPECTED_OK);
        return false;
    }
    return true;
}

bool Walbi::connect()
{
    while(!this->is_connected)
    {
        write_message(CONNECT);
        wait_for_bytes(1, 1000);
        this->handle_messages_from_serial();
    }
    return this->is_connected;
}

bool Walbi::receive_action(Action* action, bool listen_for_message)
{
    if (listen_for_message)
    {
        wait_for_serial();
        Message message_received = read_message();
        if(message_received != ACTION)
        {
            write_message(ERROR);
            write_i8(EXPECTED_ACTION);
            return false;
        }
    }
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        action->commands[i][0] = read_i16(); // position
        action->commands[i][1] = read_i16(); // span
    }
    write_message(OK);
    return true;
}

void Walbi::act(Action* action)
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        this->bus_->MoveTime(this->motor_ids[i], action->commands[i][0], action->commands[i][1]);
    }
}

State Walbi::get_state()
{
    State state;
    state.timestamp = millis();
    this->read_positions_from_debug_board_(&state);
    state.reward = 0;
    state.done = 0;
    return state;
}

bool Walbi::send_state(State* state)
{
    write_message(STATE);
    write_i32(state->timestamp);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(state->positions[i]);
    }
    write_i16(state->reward);
    write_i8(state->done);
    return wait_acknowledge();
}

bool Walbi::handle_messages_from_serial()
{
    if(Serial.available() > 0) // non blocking, do not use wait_for_serial
    {
        Message message_received = read_message(); // The first byte received is the instruction
        switch(message_received)
        {
            case CONNECT:
            {
                // If the we have not said hello, check the connection
                if(!this->is_connected)
                {
                    this->is_connected = true;
                    write_message(CONNECT);
                }
                else
                {
                    // If we are already connected do not send "connect" to avoid infinite loop
                    write_message(ALREADY_CONNECTED);
                }
                return true;
            }
            case ALREADY_CONNECTED: { this->is_connected = true; break; }
            case RESET:
            {
                write_message(OK);
                State state = this->get_state();
                return this->send_state(&state);
            }
            case STEP:
            {
                write_message(OK);
                Action action;
                if (this->receive_action(&action, true))
                {
                    this->act(&action);
                    State state = this->get_state();
                    return this->send_state(&state);
                }
                else
                {
                    return false; // receiving action has failed
                }
            }
            case ACTION:
            {
                // only happens if agent is controlling without reading state
                // we answer OK and then are expecting ACTION again
                Action action;
                return this->receive_action(&action, false);
            }
            case STATE:
            {
                write_message(OK);
                State state = this->get_state();
                return this->send_state(&state);
            }
            case VERSION:
            {
                int8_t version = read_i8();
                write_message(OK);
                write_message(VERSION);
                write_i8(PROTOCOL_VERSION);
                return wait_acknowledge();
            }
            case INFO:
            {
                write_message(ERROR);
                write_i8(NOT_IMPLEMENTED_YET);
                return false;
            }
            case CLOSE:
            {
                write_message(ERROR);
                write_i8(NOT_IMPLEMENTED_YET);
                return false;
            }
            case OK:
            {
                write_message(ERROR);
                write_i8(DID_NOT_EXPECT_OK);
                return false;
            }
            // Unknown message
            default:
            {
                write_message(ERROR);
                write_i8(RECEIVED_UNKNOWN_MESSAGE);
                return false;
            }
        }
    }
}

Walbi::Walbi(uint8_t DEBUG_BOARD_RX, uint8_t DEBUG_BOARD_TX, long COMPUTER_SERIAL_BAUD, bool auto_connect)
{
    this->mySerial_ = new SoftwareSerial(DEBUG_BOARD_TX, DEBUG_BOARD_RX); // our RX is connected to the Debug Board TX
    this->mySerial_->begin(SOFTWARE_SERIAL_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
    this->bus_ = new ServoBus(this->mySerial_, 0);
    this->bus_->setEventHandler(REPLY_POSITION, receive_position_from_debug_board_);
    Serial.begin(COMPUTER_SERIAL_BAUD);
    memcpy(this->motor_ids, MOTOR_IDS, sizeof(this->motor_ids)); // init ids with MOTOR_IDS
    if (auto_connect) { this->connect(); }
}

} // namespace
