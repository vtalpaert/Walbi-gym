from gym.error import Error

from walbi_gym.communication.settings import ERROR_CODES


class WalbiError(Error):
    """Base class for WalbiEnv errors"""


class WalbiCommunicationError(WalbiError):
    pass


class WalbiArduinoError(WalbiError):
    def __init__(self, code, *args):
        self.code = code
        message = ERROR_CODES[code] if code in ERROR_CODES else ERROR_CODES[-1]
        super().__init__(message, code, *args)


class WalbiTimeoutError(WalbiError):
    def __init__(self, timeout, expecting=(), *args):
        self.timeout = timeout
        self.message = 'Nothing received within {} seconds'.format(timeout)
        if expecting:
            self.message += ' (expecting {!r})'.format(expecting)
        super().__init__(self.message, timeout, *args)


class WalbiUnexpectedMessageError(WalbiError):
    pass
