#include <Arduino.h>
#include <SoftwareSerial.h>

#include "message.h"
#include "slave.h"
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


Message read_message()
{
	return (Message) Serial.read();
}

void wait_for_bytes(int num_bytes, unsigned long timeout)
{
	unsigned long startTime = millis();
	//Wait for incoming bytes or exit if timeout
	while ((Serial.available() < num_bytes) && (millis() - startTime < timeout)){}
}

// NOTE : Serial.readBytes is SLOW
// this one is much faster, but has no timeout
void read_signed_bytes(int8_t* buffer, size_t n)
{
	size_t i = 0;
	int c;
	while (i < n)
	{
		c = Serial.read();
		if (c < 0) break;
		*buffer++ = (int8_t) c; // buffer[i] = (int8_t)c;
		i++;
	}
}

int8_t read_i8()
{
    wait_for_bytes(1, 100); // Wait for 1 byte with a timeout of 100 ms
    return (int8_t) Serial.read();
}

int16_t read_i16()
{
    int8_t buffer[2];
	wait_for_bytes(2, 100); // Wait for 2 bytes with a timeout of 100 ms
	read_signed_bytes(buffer, 2);
    return (((int16_t) buffer[0]) & 0xff) | (((int16_t) buffer[1]) << 8 & 0xff00);
}

int32_t read_i32()
{
    int8_t buffer[4];
	wait_for_bytes(4, 200); // Wait for 4 bytes with a timeout of 200 ms
	read_signed_bytes(buffer, 4);
    return (((int32_t) buffer[0]) & 0xff) | (((int32_t) buffer[1]) << 8 & 0xff00) | (((int32_t) buffer[2]) << 16 & 0xff0000) | (((int32_t) buffer[3]) << 24 & 0xff000000);
}

void write_message(enum Message myMessage)
{
	uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

void write_i8(int8_t num)
{
    Serial.write(num);
}

void write_i16(int16_t num)
{
	int8_t buffer[2] = {(int8_t) (num & 0xff), (int8_t) (num >> 8)};
    Serial.write((uint8_t*)&buffer, 2*sizeof(int8_t));
}

void write_i32(int32_t num)
{
	int8_t buffer[4] = {(int8_t) (num & 0xff), (int8_t) (num >> 8 & 0xff), (int8_t) (num >> 16 & 0xff), (int8_t) (num >> 24 & 0xff)};
    Serial.write((uint8_t*)&buffer, 4*sizeof(int8_t));
}
