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

void receive_position_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    (void)id;
    (void)command;
    (void)param2;
    last_received_position_ = param1;
}

Walbi::Walbi(uint8_t DEBUG_BOARD_RX, uint8_t DEBUG_BOARD_TX, long COMPUTER_SERIAL_BAUD, bool auto_connect)
{
    this->mySerial_ = new SoftwareSerial(DEBUG_BOARD_TX, DEBUG_BOARD_RX); // our RX is connected to the Debug Board TX
    this->mySerial_->begin(SOFTWARE_SERIAL_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
    this->bus_ = new ServoBus(this->mySerial_, 0);
    this->bus_->setEventHandler(REPLY_POSITION, receive_position_);
    Serial.begin(COMPUTER_SERIAL_BAUD);
    memcpy(this->motor_ids, MOTOR_IDS, sizeof(this->motor_ids)); // init ids with MOTOR_IDS
    if (auto_connect) { this->connect(); }
}

bool Walbi::connect()
{
    while(!this->is_connected)
    {
        write_message(CONNECT);
        wait_for_bytes(1, 1000);
        this->get_messages_from_serial();
    }
    return this->is_connected;
}

void wait_for_serial() // blocking
{
    while (Serial.available() == 0) { delay(1); }
}

void Walbi::read_positions()
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        this->bus_->requestPosition(this->motor_ids[i]);
        this->positions[i] = last_received_position_;
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

bool Walbi::action()
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        int16_t position = read_i16();
        int16_t span = read_i16();
        this->bus_->MoveTime(this->motor_ids[i], position, span);
    }
    write_message(OK);
    return true;
}

bool Walbi::observation()
{
    this->collect_observation(); // TODO don't do it here
    write_message(OBSERVATION);
    delta = timestamp_gathered_observation - timestamp_successfully_sent_observation;
    if (delta > this->timestamp_delta_highest_allowed_)
    {
        delta = this->timestamp_delta_timeout_signal_;
    }
    write_i16(delta);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(this->positions[i]);
    }
    if (wait_acknowledge())
    {
        timestamp_successfully_sent_observation = timestamp_gathered_observation;
        return true;
    } else
    {
        return false;
    }
}

bool timestamp_observation()
{
    write_message(TIMESTAMP_OBSERVATION);
    write_i32(timestamp_successfully_sent_observation);
    return wait_acknowledge();
}

bool Walbi::reward()
{
    int16_t reward = 0;
    int8_t done = 0;
    write_message(REWARD);
    write_i16(reward);
    write_i8(done);
    return wait_acknowledge();
}

bool Walbi::step()
{
    write_message(OK);
    wait_for_serial();
    Message message_received = read_message();
    if(message_received == ACTION)
    {
        if(action()) { if(this->observation()) { return this->reward(); } }
        return false;
    }
    else
    {
        write_message(ERROR);
        write_i8(EXPECTED_ACTION);
        return false;
    }
}

bool Walbi::reset()
{
    write_message(OK);
    return this->observation();
}

void Walbi::get_messages_from_serial()
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
                break;
            }
            case ALREADY_CONNECTED: { this->is_connected = true; break; }
            case RESET: { this->reset(); break; }
            case STEP: { this->step(); break; }
            case ACTION: { this->action(); break; }
            case OBSERVATION: { this->observation(); break; }
            case TIMESTAMP_OBSERVATION: { timestamp_observation(); break; }
            // Throw some errors
            case INFO:
            {
                write_message(ERROR);
                write_i8(NOT_IMPLEMENTED_MESSAGE);
            }
            case CLOSE:
            {
                write_message(ERROR);
                write_i8(NOT_IMPLEMENTED_MESSAGE);
            }
            case OK:
            {
                write_message(ERROR);
                write_i8(DID_NOT_EXPECT_OK);
            }
            // Unknown message
            default:
            {
                write_message(ERROR);
                write_i8(RECEIVED_UNKNOWN_MESSAGE);
                return;
            }
        }
    }
}

void Walbi::collect_observation()
{
    timestamp_gathered_observation = millis();
    this->read_positions();
}

void Walbi::run_once()
{
    // do some things, like
    //this->collect_observation(); // uncomment when not done inside observation
    this->get_messages_from_serial();
}

} // namespace
