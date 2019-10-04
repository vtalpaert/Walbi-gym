from enum import IntEnum

PROTOCOL_VERSION = 4  # int: protocol version

class Message(IntEnum):
    """
    Pre-defined messages
    """
    OK = 1
    NOK = 2
    CONNECT = 3
    ALREADY_CONNECTED = 4
    RESET = 5
    STEP = 6
    ACTION = 7
    STATE = 8
    CLOSE = 9
    INFO = 10
    ERROR = 11
    VERSION = 12

ERROR_CODES = {  # must be coherent with what Walbi.cpp throws
    -1: 'UNKNOWN_ERROR_CODE',
    0: 'RECEIVED_UNKNOWN_MESSAGE',
    1: 'EXPECTED_OK',
    2: 'DID_NOT_EXPECT_OK',
    3: 'DID_NOT_EXPECT_NOK',
    4: 'DID_NOT_EXPECT_MESSAGE',
    5: 'NOT_IMPLEMENTED_YET',
}

MESSAGE_TYPES = {
    Message.STEP: [['int16', 'int16']] * 10,  # two values per motor # for Message.ACTION as well
    Message.STATE: ['int32'] + ['int16', 'int8'] * 10,  # ts, 10 * (position, is_position_updated)
    Message.ERROR: ['int8'],  # error code
    Message.VERSION: ['int8'],
}
MESSAGE_TYPES[Message.ACTION] = MESSAGE_TYPES[Message.STEP]
