import time
import logging
from .base_agent import BaseAgent
from threading import Thread
from config import constants

class MAAgent(BaseAgent):
    
        def __init__(self):
            super().__init__()
    
        def run(self):
            while True:
                self.signal()
                time.sleep(constants.TICK)
    
        def signal(self):
            self.lock.acquire()
            logging.info(f'Here {self.__str__()}')
            self.lock.release()
