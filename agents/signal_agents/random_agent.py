import time
import logging
import random
from .base_signal_agent import BaseSignalAgent
from threading import Thread
from config import constants

class RandomAgent(BaseSignalAgent):
    
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)

    def signal(self):
        self.lock.acquire()
        self.signals.append(float(random.randint(-1, 1)))
        self.updated = True
        logging.info(f'Random Signal: {self.signals[-1]}')
        self.lock.release()