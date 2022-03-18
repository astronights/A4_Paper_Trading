from agents import ceo_agent
from .base_agent import BaseAgent
from config import constants
import time
import logging
from utils.io_utils import Type

class DeciderAgent(BaseAgent):

    def __init__(self, signal_agents, dao_agent, ceo_agent):
        super().__init__()
        self.signal_agents = signal_agents
        self.dao_agent = dao_agent
        self.ceo_agent = ceo_agent
        self.trade = {}
        
    def run(self):
        while True:
            self.decide()
            time.sleep(constants.TICK)

    def decide(self):
        self.lock.acquire()
        #TODO: Calculate action and quantity using some algorithm
        weights = self.dao_agent.get_last_data(Type.AGENT_WEIGHTS).to_dict()
        latest_actions = dict([(agent.__str__(), agent.latest()) for agent in self.signal_agents])
        action = [weights[agent_name] * latest_actions[agent_name] for agent_name in weights.keys()]
        self.trade['action'] = action
        self.trade['quantity'] = 10.0
        self.ceo_agent.make_trade(self.trade)
        logging.info(f'Trade Decided: {self.trade}')
        self.lock.release()
        
