import bluetooth

from .socket_interface import SocketInterface, SocketServerInterface


class BluetoothServerInterface(SocketServerInterface):
    def __init__(self, host_address='', port=1, backlog=1):
        # show mac address: hciconfig
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_socket.bind((host_address, port))
        self.server_socket.listen(backlog)
        super().__init__()


class BluetoothClientInterface(SocketInterface):
    def __init__(self, client_address, port=1):
        self.client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.client_address = client_address
        self.port = port
        super().__init__()
    
    def _set_client(self):
        self.client_socket.connect((self.client_address, self.port))
