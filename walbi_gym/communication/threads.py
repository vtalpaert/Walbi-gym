import threading
import time
import weakref
try:
    import queue
except ImportError:
    import Queue as queue

from walbi_gym.envs.definitions import Message
from walbi_gym.envs.definitions import RATE as rate


# From https://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue
class CustomQueue(queue.Queue):
    """
    A custom queue subclass that provides a :meth:`clear` method.
    """

    def clear(self):
        """
        Clears all items from the queue.
        """

        with self.mutex:
            unfinished = self.unfinished_tasks - len(self.queue)
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
            self.queue.clear()
            self.not_full.notify_all()


class CommandThread(threading.Thread):
    """
    Thread that send messages to the Arduino
    :param parent: will call send_message on parent (Interface object)
    :param command_queue: (Queue)
    :param exit_event: (Threading.Event object)
    :param lock: (threading.Lock)
    """

    def __init__(self, parent, command_queue, exit_event, lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.parent = weakref.proxy(parent)
        self.command_queue = command_queue
        self.exit_event = exit_event
        self.lock = lock

    def run(self):
        while not self.exit_event.is_set():
            if self.exit_event.is_set():
                break
            try:
                message, param = self.command_queue.get_nowait()
            except queue.Empty:
                time.sleep(rate)
                continue

            with self.lock:
                self.parent._send_message(message, param)
            time.sleep(rate)
        print('Command Thread Exited')


class ListenerThread(threading.Thread):
    """
    Thread that listen to the Arduino
    :param parent: will call handle_message on parent (Interface object)
    :param exit_event: (threading.Event object)
    :param lock: (threading.Lock)
    """

    def __init__(self, parent, serial_file, exit_event, lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.parent = weakref.proxy(parent)
        self.serial_file = serial_file
        self.exit_event = exit_event
        self.lock = lock

    def run(self):
        while not self.exit_event.is_set():
            byte = self.parent._read_byte()
            if byte is None:
                continue
            with self.lock:
                try:
                    message = Message(byte)
                except ValueError:
                    continue
                self.parent._handle_message(message)
            time.sleep(rate)
        print('Listener Thread Exited')
