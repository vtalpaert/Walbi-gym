__dependency_name__ = 'bluetooth'

try:
    import bluetooth
    __has_bluetooth__ = True
except ImportError:
    __has_bluetooth__ = False

from .socket_interface import SocketInterface, SocketServerInterface
from walbi_gym.envs.errors import dependency_required


class BluetoothServerInterface(SocketServerInterface):
    @dependency_required(dependency=__dependency_name__, condition=__has_bluetooth__)
    def __init__(self, host_address='', port=1, backlog=1):
        # show mac address: hciconfig
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_socket.bind((host_address, port))
        self.server_socket.listen(backlog)
        super().__init__()


class BluetoothClientInterface(SocketInterface):
    @dependency_required(dependency=__dependency_name__, condition=__has_bluetooth__)
    def __init__(self, client_address, port=1):
        self.client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.client_address = client_address
        self.port = port
        super().__init__()
    
    def _set_client(self):
        self.client_socket.connect((self.client_address, self.port))
