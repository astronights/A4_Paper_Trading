from abc import ABC, abstractmethod
from threading import Thread, Lock
import logging

"""Base Agent to provide common functionality for all agents"""
class BaseAgent(ABC):

    def __init__(self):
        self.lock = Lock()

        # Generate threads to run in the background
        self.thread = Thread(name = self.__str__(), target = self.run)
        self.thread.daemon = True
        self.updated = False
        logging.info(f'Created {self.__str__()}')

    @abstractmethod
    def run(self):
        pass

    """Start running the thread for the agent"""
    def start(self):
        logging.info(f'Starting {self.__str__()}')
        self.thread.start()

    """Stop running the thread for clean exit"""
    def stop(self):
        logging.info(f'Stopping {self.__str__()}')

    """Get the name of the agent"""
    def __str__(self):
        return self.__class__.__name__
