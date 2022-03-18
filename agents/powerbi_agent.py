from .base_agent import BaseAgent
import time
from config import constants

class PowerBIAgent(BaseAgent):
    
        def __init__(self, broker_agent, dao_agent):
            super().__init__()
            self.broker_agent = broker_agent
            self.dao_agent = dao_agent
    
        def run(self):
            while True:
                self.update()
                time.sleep(constants.TICK)
    
        def update(self):
            #TODO Build objects to send to powerBI
            pass