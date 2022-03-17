from abc import ABC, abstractmethod
from threading import Lock

class BaseAgent(ABC):

    def __init__(self):
        self.lock = Lock()
        self.signals = []

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def signal(self):
        pass

    @abstractmethod
    def latest(self):
        pass


    def __str__(self):
        return self.__class__.__name__
