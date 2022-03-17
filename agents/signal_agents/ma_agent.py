import time
from base_agent import BaseAgent
from threading import Thread,Lock
from config import constants

class MAAgent(BaseAgent):
    
        def __init__(self):
            self.signals = []
            self.thread = Thread(name = self.__str__(), target = self.run)
            self.thread.start()
    
        def run(self):
            while True:
                self.tick()
                time.sleep(constants.TICK)
    
        def signal(self):
            print(f'Here {self.__str__()}')
