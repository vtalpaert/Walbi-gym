from enum import IntEnum

PROTOCOL_VERSION = 7  # int: protocol version

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
    6: 'SENSOR_ERROR_WEIGHT',
    7: 'SENSOR_ERROR_IMU',
}

MESSAGE_TYPES = {
    Message.STEP: [['int16', 'int16', 'int16']] * 10,  # three values per motor [position, span, activate] # for Message.ACTION as well
    # STATE: ts, [position, is_position_updated] * 10, correct_motor_reading, weight * 2, imu * 9
    Message.STATE: ['int32'] + ['int16', 'int8'] * 10 + ['int8', 'int32', 'int32'] + ['int16'] * 9,
    Message.ERROR: ['int8'],  # error code
    Message.VERSION: ['int8'],
}
MESSAGE_TYPES[Message.ACTION] = MESSAGE_TYPES[Message.STEP]
