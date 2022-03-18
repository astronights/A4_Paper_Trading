from abc import ABC, abstractmethod
from threading import Thread, Lock
import logging
class BaseAgent(ABC):

    def __init__(self):
        self.lock = Lock()
        self.thread = Thread(name = self.__str__(), target = self.run)
        self.thread.daemon = True
        logging.info(f'Created {self.__str__()}')

    @abstractmethod
    def run(self):
        pass

    def start(self):
        logging.info(f'Starting {self.__str__()}')
        self.thread.start()

    def stop(self):
        logging.info(f'Stopping {self.__str__()}')
        # self.thread.join()

    def __str__(self):
        return self.__class__.__name__
