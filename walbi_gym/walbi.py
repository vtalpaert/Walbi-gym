import numpy as np

from walbi_gym.protocol import Message, PROTOCOL_VERSION
from walbi_gym import errors
from walbi_gym.communication import BaseInterface, make_interface
from walbi_gym.configuration import config


class Walbi(object):
    protocol_version = PROTOCOL_VERSION
    config = config

    def __init__(self, interface='serial', autoconnect=True, verify_version=True, *args, **kwargs):
        self.interface = make_interface(interface, *args, **kwargs)
        self.settings = None
        if autoconnect and not self.interface.is_connected:
            self.interface.connect()
        if verify_version and self.interface.is_connected and self.interface.verify_version():
            print('Version OK')

    def send_action(self, int16_action):
        self.interface.put_command(Message.ACTION, param=int16_action, expect_ok=True)

    def apply_settings(self, interval_send_state_millis):
        self.settings = (interval_send_state_millis,)
        self.interface.put_command(Message.SET, param=self.settings, expect_ok=True)

    def read_message(self, block=True, timeout=None):
        return self.interface.queue.get(block=block, timeout=timeout)

    def get_last_state(self, raise_if_error=True):
        while not self.interface.queue.empty():
            message, values = self.read_message()
            if message == Message.STATE:
                state = values
            else:
                if message == Message.ERROR:
                    error = errors.WalbiArduinoError(param[0])
                else:
                    error = WalbiUnexpectedMessageError(message, Message.STATE)
                if raise_if_error:
                    raise error
                else:
                    print(error)
        return state

    def close(self):
        if self.interface.is_connected:
            self.interface.close()


if __name__ == '__main__':
    pass
