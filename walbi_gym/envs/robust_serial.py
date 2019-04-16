from __future__ import print_function, division, unicode_literals, absolute_import

import struct

from enum import IntEnum


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


def read_message(f):
    """
    :param f: file handler or serial file
    :return: (Message Enum Object)
    """
    return Message(read_i8(f))


def write_message(f, message):
    """
    :param f: file handler or serial file
    :param message: (Message Enum Object)
    """
    write_i8(f, message.value)


def read_i8(f):
    """
    :param f: file handler or serial file
    :return: (int8_t)
    """
    return struct.unpack('<b', bytearray(f.read(1)))[0]


def read_i16(f):
    """
    :param f: file handler or serial file
    :return: (int16_t)
    """
    return struct.unpack('<h', bytearray(f.read(2)))[0]


def read_i32(f):
    """
    :param f: file handler or serial file
    :return: (int32_t)
    """
    return struct.unpack('<l', bytearray(f.read(4)))[0]


def write_i8(f, value):
    """
    :param f: file handler or serial file
    :param value: (int8_t)
    """
    if -128 <= value <= 127:
        f.write(struct.pack('<b', value))
    else:
        print("Value error:{}".format(value))


def write_i16(f, value):
    """
    :param f: file handler or serial file
    :param value: (int16_t)
    """
    f.write(struct.pack('<h', value))


def write_i32(f, value):
    """
    :param f: file handler or serial file
    :param value: (int32_t)
    """
    f.write(struct.pack('<l', value))
