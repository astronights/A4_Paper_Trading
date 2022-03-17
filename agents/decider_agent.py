from .base_agent import BaseAgent
from config import constants
import time

class DeciderAgent(BaseAgent):

    def __init__(self, agents):
        super().__init__()
        self.agents = agents
        self.trade = {}
        
    def run(self):
        while True:
            self.decide()
            time.sleep(constants.TICK)

    def decide(self):
        action = max([agent.latest() for agent in self.agents])
        self.trade['action'] = action
        
