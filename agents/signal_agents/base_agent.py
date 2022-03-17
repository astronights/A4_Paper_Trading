from abc import ABC, abstractmethod
from threading import Thread, Lock

class BaseAgent(ABC):

    def __init__(self):
        self.lock = Lock()
        self.signals = []
        self.thread = Thread(name = self.__str__(), target = self.run)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.join()

    @abstractmethod
    def signal(self):
        pass

    def latest(self):
        return self.signals[-1] if(len(self.signals) > 0) else 0

    def __str__(self):
        return self.__class__.__name__
