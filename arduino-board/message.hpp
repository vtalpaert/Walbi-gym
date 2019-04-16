#ifndef MESSAGE_H
#define MESSAGE_H

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

Message read_message()
{
	return (Message) Serial.read();
}

void write_message(enum Message myMessage)
{
	uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

#endif
