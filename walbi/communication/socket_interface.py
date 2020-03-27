import socket
from abc import ABC
from warnings import warn

from walbi.communication.base import BaseInterface


class SocketInterface(BaseInterface, ABC):
    client_socket = None
    client_address = None

    def _set_client(self):
        raise NotImplementedError()

    def connect(self):
        self._set_client()
        if self.client_socket:
            print('Buetooth client detected over address %s' % self.client_address)
            # Rename function to work with the lib
            self.client_socket.read = self.client_socket.recv
            self.client_socket.write = self.client_socket.send

            self.file = self.client_socket
            super().connect()


class SocketServerInterface(SocketInterface):
    def __init__(self, host_address='', port=1, backlog=1):
        warn('This interface has not been tested')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host_address, port))
        self.server_socket.listen(backlog)
        super().__init__()

    def _set_client(self):
        self.client_socket, self.client_address = self.server_socket.accept()

    def close(self):
        super().close()
        print("Closing server socket")	
        self.server_socket.close()
