#include "Walbi.h"

namespace Walbi
{

Message read_message()
{
	return (Message) Serial.read();
}

void write_message(enum Message myMessage)
{
	uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

uint16_t last_received_position_;

void receive_position_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    (void)id;
    (void)command;
    (void)param2;
    last_received_position_ = param1;
}

Walbi::Walbi(uint8_t DEBUG_BOARD_RX, uint8_t DEBUG_BOARD_TX, long COMPUTER_SERIAL_BAUD, bool auto_connect)
{
    this->mySerial_ = new SoftwareSerial(DEBUG_BOARD_RX, DEBUG_BOARD_TX);
    this->mySerial_->begin(SOFTWARE_SERIAL_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
    this->bus_ = new ServoBus(this->mySerial_, 0);
    this->bus_->setEventHandler(REPLY_POSITION, receive_position_);
    Serial.begin(COMPUTER_SERIAL_BAUD);

    memcpy(this->motor_ids, MOTOR_IDS, sizeof(this->motor_ids)); // init ids with MOTOR_IDS

    if (auto_connect)
    {
        this->connect();
    }
}

void non_blocking_delay(unsigned long interval)
{
    unsigned long start_millis = millis();
    while (millis() - start_millis < interval) { delay(10); }
}

void wait_for_serial()
{
    while (Serial.available() == 0) { non_blocking_delay(1); }
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
        write_i8(2);
        return false;
    }
    return true;
}

bool Walbi::action()
{
    wait_for_serial();
    Message message_received = read_message();
    if(message_received == ACTION)
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
    else
    {
        write_message(ERROR);
        write_i8(1);
        return false;
    }
}

bool Walbi::observation()
{
    this->read_positions();
    write_message(OBSERVATION);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(this->positions[i]);
    }
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
    if(action()) { if(this->observation()) { return this->reward(); } }
    return false;
}

bool Walbi::reset()
{
    write_message(OK);
    return this->observation();
}

void Walbi::get_messages_from_serial()
{
    if(Serial.available() > 0)
    {
        Message message_received = read_message(); // The first byte received is the instruction
        if(message_received == CONNECT)
        {
            // If the cards haven't said hello, check the connection
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
        }
        else if(message_received == ALREADY_CONNECTED)
        {
            this->is_connected = true;
        }
        else
        {
            switch(message_received)
            {
                case RESET: { this->reset(); break; }
                case STEP: { this->step(); break; }
                case OBSERVATION: { this->observation(); break; }
                // Unknown message
                default:
                {
                    write_message(ERROR);
                    write_i8(0);
                    return;
                }
            }
        }
    }
}

bool Walbi::connect()
{
    while(!this->is_connected)
    {
        write_message(CONNECT);
        wait_for_bytes(1, 1000);
        get_messages_from_serial();
    }
    return this->is_connected;
}

} // namespace
