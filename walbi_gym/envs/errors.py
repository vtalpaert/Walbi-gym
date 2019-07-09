import inspect

from gym.error import Error

from walbi_gym.envs.definitions import ERROR_CODES


class WalbiError(Error):
    """Base class for WalbiEnv errors"""


class WalbiCommunicationError(WalbiError):
    pass


class WalbiProtocolVersionError(WalbiCommunicationError):
    """Mismatch between local and distant protocol version"""


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
     def __init__(self, received_message, expected_message=None, *args):
        self.received_message = received_message
        self.expected_message = expected_message
        message = 'Expected %s but got %s' % (expected_message, received_message)
        super().__init__(message, received_message, *args)


class WalbiMissingDependencyError(Error):
    """Error when missing optionnal dependency"""
    def __init__(self, dependency, *args):
        message = 'You are missing a dependency, run "pip install -e .[%s]"' % str(dependency)
        super().__init__(message, *args)


def dependency_required(*, dependency, condition):
    def decorator(fn):
        def decorated(*args, **kwargs):
            if condition:
                return fn(*args, **kwargs)
            raise WalbiMissingDependencyError(dependency)
        return decorated
    return decorator
