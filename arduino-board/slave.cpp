#include <Arduino.h>
#include <SoftwareSerial.h>

#include "robust_serial.h"
#include "message.hpp"
#include "parameters.h"
#include "ServoBus.h"

bool is_connected = false;  // True if the connection with the master is available

SoftwareSerial mySerial(SOFT_RX, SOFT_TX);
ServoBus bus(&mySerial, 0);

uint16_t positions[MOTOR_NB];
uint16_t last_received_position;

void receive_positions()
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        bus.requestPosition(MOTOR_IDS[i]);
        positions[i] = last_received_position;
    }
}

void receive_position(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    last_received_position = param1;
}

void action()
{
    Message message_received = read_message();
    if(message_received == ACTION)
    {
        for (uint8_t i = 0; i < MOTOR_NB; i++)
        {
            int16_t position = read_i16();
            int16_t span = read_i16();
            bus.MoveTime(MOTOR_IDS[i], position, span);
        }
    }
    else
    {
        write_message(ERROR);
        write_i8(1);
    }
}

void observation()
{
    receive_positions();
    write_message(OBSERVATION);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(positions[i]);
    }
}

void reward()
{
    int16_t reward = 0;
    int8_t done = 0;
    write_message(REWARD);
    write_i16(reward);
    write_i8(done);
}

void get_messages_from_serial()
{
    if(Serial.available() > 0)
    {
        // The first byte received is the instruction
        Message message_received = read_message();

        if(message_received == CONNECT)
        {
            // If the cards haven't say hello, check the connection
            if(!is_connected)
            {
                is_connected = true;
                write_message(CONNECT);
            }
            else
            {
                // If we are already connected do not send "hello" to avoid infinite loop
                write_message(ALREADY_CONNECTED);
            }
        }
        else if(message_received == ALREADY_CONNECTED)
        {
            is_connected = true;
        }
        else
        {
            switch(message_received)
            {
                case RESET:
                {
                    observation();
                    break;
                }
                case STEP:
                {
                    action();
                    observation();
                    reward();
                }
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

void setup()
{
    bus.setEventHandler(REPLY_POSITION, receive_position);

    // Init Serial
    Serial.begin(SERIAL_BAUD);

    mySerial.begin(SOFTWARE_SERIAL_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)

    // Wait until the arduino is connected to master
    while(!is_connected)
    {
        write_message(CONNECT);
        wait_for_bytes(1, 1000);
        get_messages_from_serial();
    }
}

void loop()
{
    get_messages_from_serial();
}
