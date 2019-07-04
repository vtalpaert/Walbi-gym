from enum import IntEnum

PROTOCOL_VERSION = 4  # int: protocol version

RATE = 1 / 2000  # 2000 Hz (limit the rate of communication with the arduino)

COMMUNICATION_DELAY = 0
COMMUNICATION_TIMEOUT = 0.5

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

MOTOR_RANGES = {  # ((min_position, min_span), (max_position, max_span))
        0: ((210, 0), (745, 1000)),
        1: ((367, 0), (569, 1000)),
        2: ((423, 0), (1000, 1000)),
        3: ((607, 0), (886, 1000)),
        4: ((157, 0), (868, 1000)),
        5: ((103, 0), (659, 1000)),
        6: ((560, 0), (681, 1000)),
        7: ((0, 0), (595, 1000)),
        8: ((372, 0), (630, 1000)),
        9: ((179, 0), (888, 1000)),
    }

MESSAGE_TYPES = {
    Message.STEP: [['int16', 'int16']] * 10,  # two values per motor # for Message.ACTION as well
    Message.STATE: ['int32'] + ['int16', 'int8'] * 10,  # ts, 10 * (position, is_position_updated)
    Message.ERROR: ['int8'],  # error code
    Message.VERSION: ['int8'],
}
MESSAGE_TYPES[Message.ACTION] = MESSAGE_TYPES[Message.STEP]


# spaces definitions
MOTOR_RANGES_LOW, MOTOR_RANGES_HIGH = list(zip(*tuple(MOTOR_RANGES.values())))
POSITIONS_LOW, _ = tuple(zip(*MOTOR_RANGES_LOW))
POSITIONS_HIGH, _ = tuple(zip(*MOTOR_RANGES_HIGH))

RAW_OBSERVATION_LOW = list(POSITIONS_LOW)
RAW_OBSERVATION_HIGH = list(POSITIONS_HIGH)
OBSERVATION_SHAPE = (10,)
RAW_ACTION_LOW, RAW_ACTION_HIGH = MOTOR_RANGES_LOW, MOTOR_RANGES_HIGH
ACTION_SHAPE = (10, 2)
