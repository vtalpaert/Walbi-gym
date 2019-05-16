from enum import IntEnum


RATE = 1 / 2000  # 2000 Hz (limit the rate of communication with the arduino)


class Message(IntEnum):
    """
    Pre-defined messages
    """
    OK = 1
    CONNECT = 2
    ALREADY_CONNECTED = 3
    RESET = 4
    STEP = 5
    ACTION = 6
    OBSERVATION = 7
    REWARD = 8  # reward and termination
    CLOSE = 9
    CONFIG = 10
    ERROR = 11


ERROR_CODES = {  # must be coherent with arduino-board/slave.cpp throws
    -1: 'UNKNOWN_ERROR_CODE',
    0: 'RECEIVED_UNKNOWN_MESSAGE',
    1: 'EXPECTED_ACTION',
    2: 'EXPECTED_OK',
}


MESSAGE_TYPES = {
    Message.ACTION: ['int16'] * 20,
    Message.OBSERVATION: ['int16'] * 10,
    Message.REWARD: ['int16', 'int8'],
    Message.ERROR: ['int8']
}
