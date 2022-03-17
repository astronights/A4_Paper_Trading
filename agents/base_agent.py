from abc import ABC, abstractmethod
from threading import Thread, Lock
import logging
class BaseAgent(ABC):

    def __init__(self):
        logging.info(f'{self.__str__()} created...')
        self.lock = Lock()
        self.thread = Thread(name = self.__str__(), target = self.run)
        self.thread.daemon = True

    @abstractmethod
    def run(self):
        pass

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.join()

    def __str__(self):
        return self.__class__.__name__
