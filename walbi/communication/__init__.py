from .base import BaseInterface
from .serial_interface import SerialInterface
from .bluetooth_interface import BluetoothClientInterface, BluetoothServerInterface
from .socket_interface import SocketServerInterface


INTERFACE_CLASS_MAPPING = {
    'serial': SerialInterface,
    'socket_server': SocketServerInterface,
    'bluetooth_client': BluetoothClientInterface,
    'bluetooth_server': BluetoothServerInterface,
}

def make_interface(interface, *args, **kwargs):
    if isinstance(interface, BaseInterface):
        return interface
    elif interface in INTERFACE_CLASS_MAPPING:
        return INTERFACE_CLASS_MAPPING[interface](*args, **kwargs)
    else:
        raise NotImplementedError('%s is not implemented yet, choose from %s' % (interface, INTERFACE_CLASS_MAPPING.keys()))
