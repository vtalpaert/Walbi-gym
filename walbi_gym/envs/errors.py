ERROR_CODES = {  # must be coherent with arduino-board/slave.cpp throws
    -1: 'UNKNOWN_ERROR_CODE',
    0: 'RECEIVED_UNKNOWN_MESSAGE',
    1: 'EXPECTED_ACTION',
    2: 'EXPECTED_OK',
}


class WalbiError(ConnectionError):
    """Base class for WalbiEnv errors"""


class WalbiArduinoError(WalbiError):
    def __init__(self, code, *args):
        self.code = code
        message = ERROR_CODES[code] if code in ERROR_CODES else ERROR_CODES[-1]
        super().__init__(message, *args)


class WalbiTimeoutError(WalbiError):
    def __init__(self, timeout, expecting, *args):
        self.timeout = timeout
        self.message = 'Nothing received within %fs (expecting %s)'\
                       % (timeout, list(map(str, expecting)))
        super().__init__(self.message, *args)


class WalbiUnexpectedMessageError(WalbiError):
    pass
