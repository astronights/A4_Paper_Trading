from .base_agent import BaseAgent
from config import constants
import time
import logging
from data_io import csv_io

class DeciderAgent(BaseAgent):

    def __init__(self, signal_agents):
        super().__init__()
        self.signal_agents = signal_agents
        self.trade = {}
        
    def run(self):
        while True:
            self.decide()
            time.sleep(constants.TICK)

    def decide(self):
        self.lock.acquire()
        #TODO: Calculate action and quantity using some algorithm
        weights = csv_io.load_last_data(csv_io.Type.AGENT_WEIGHTS).to_dict()
        latest_actions = [(agent.__str__(), agent.latest()) for agent in self.signal_agents]
        action = [weights[agent_name] * latest_actions[agent_name] for agent_name in weights.keys()]
        self.trade['action'] = action
        logging.info(f'Trade Decided: {self.trade}')
        self.lock.release()
        
