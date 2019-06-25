#include "Walbi.h"

namespace Walbi
{

Message read_message() { return (Message) Serial.read(); }

void write_message(enum Message myMessage)
{
    uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

State last_state;
unsigned long timestamp_last_handled_message = 0;

void Walbi::receive_position_from_debug_board_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    (void)command;
    (void)param2;
    last_state.positions[id] = param1; // TODO find index of array according to id, now we suppose the index and id are the same
}

void wait_for_serial() // blocking until Serial available
{
    while (Serial.available() == 0) { delay(1); }
}

State* Walbi::read_positions_from_debug_board_()
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        this->bus_->requestPosition(this->motor_ids[i]);
    }
    return &last_state;
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
        // we wait for an ACTION message
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

State* Walbi::get_state()
{
    last_state.timestamp = millis();
    this->read_positions_from_debug_board_();
    return &last_state;
}

bool Walbi::send_state(State* state)
{
    write_message(STATE);
    write_i32(state->timestamp);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(state->positions[i]);
    }
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
                State* state_ptr = this->refresh_state_if_needed_();
                return this->send_state(state_ptr);
            }
            case STEP:
            {
                Action action;
                if (this->receive_action(&action, false))
                {
                    this->act(&action);
                    State* state_ptr = this->refresh_state_if_needed_();
                    return this->send_state(state_ptr);
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
                State* state_ptr = this->refresh_state_if_needed_();
                return this->send_state(state_ptr);
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
    return false;
}

State* Walbi::refresh_state_if_needed_() {
    if(millis() - last_state.timestamp >= this->interval_refresh_state_) {
		return this->get_state();
	}
    return &last_state;
}

void Walbi::run(){
	if(millis() - timestamp_last_handled_message >= this->interval_read_serial_) {
		timestamp_last_handled_message = millis();
		this->handle_messages_from_serial();
	}
	this->refresh_state_if_needed_();
}

Walbi::Walbi(uint8_t debug_board_rx, uint8_t debug_board_tx, long computer_serial_baud, unsigned long interval_read_serial, unsigned long interval_refresh_state, bool auto_connect):
    interval_read_serial_(interval_read_serial), interval_refresh_state_(interval_refresh_state)
{
    Serial2.begin(DEBUG_BOARD_SERIAL_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
    this->bus_ = new ServoBus(Serial2, 0);
    this->bus_->setEventHandler(REPLY_POSITION, this->receive_position_from_debug_board_);
    Serial.begin(computer_serial_baud);
    memcpy(this->motor_ids, MOTOR_IDS, sizeof(this->motor_ids)); // init ids with MOTOR_IDS
    if (auto_connect) { this->connect(); }
}

} // namespace
