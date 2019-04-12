#ifndef MESSAGE_H
#define MESSAGE_H

// Define the messages that can be sent and received
enum Message {
    CONNECT = 0,
    ALREADY_CONNECTED = 1,
    RESET = 2,
    STEP = 9,
    ACTION = 3,
    OBSERVATION = 4,
    REWARD = 5,  // reward and termination
    CLOSE = 6,
    CONFIG = 7,
    ERROR = 8,
};

typedef enum Message Message;

#endif
