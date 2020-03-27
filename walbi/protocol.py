from enum import IntEnum
from collections import namedtuple

PROTOCOL_VERSION = 8  # int: protocol version

class Message(IntEnum):
    """
    Pre-defined messages
    """
    OK = 1
    CONNECT = 2
    ALREADY_CONNECTED = 3
    ERROR = 4
    VERSION = 5
    SET = 6
    ACTION = 7
    STATE = 8

ERROR_CODES = {  # must be coherent with what Walbi.cpp throws
    -1: 'UNKNOWN_ERROR_CODE',
    0: 'RECEIVED_UNKNOWN_MESSAGE',
    1: 'EXPECTED_OK',
    2: 'DID_NOT_EXPECT_OK',
    3: 'DID_NOT_EXPECT_MESSAGE',
    4: 'NOT_IMPLEMENTED_YET',
    5: 'SENSOR_ERROR_WEIGHT',
    6: 'SENSOR_ERROR_IMU',
    7: 'INCOMPLETE_MESSAGE'
}

MESSAGE_TYPES = {
    Message.ACTION: ['int16', 'int16', 'int8'] * 10,  # three values per motor [position, span, activate]
    # STATE: ts, [position, is_position_updated] * 10, correct_motor_reading, weight * 2, imu * 9
    Message.STATE: ['int32'] + ['int16', 'int8'] * 10 + ['int8', 'int32', 'int32'] + ['int16'] * 9,
    Message.ERROR: ['int8'],  # error code
    Message.VERSION: ['int8'],
    Message.SET: ['int32'],
}
