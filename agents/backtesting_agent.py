from .base_agent import BaseAgent
import time
import logging
import random
from config import constants
from utils.io_utils import Type

class BackTestingAgent(BaseAgent):

    def __init__(self, signal_agents, dao_agent):
        super().__init__()
        self.dao_agent = dao_agent
        self.signal_agents = signal_agents

    def run(self):
        while True:
            self.calculate()
            time.sleep(constants.CYCLE)

    def calculate(self):
        self.lock.acquire()
        account_book = self.dao_agent.load_all_data(Type.ACCOUNT_BOOK)
        #TODO: Update Weights using some algorithm
        weights = self.dao_agent.agent_weights.iloc[-1].to_dict()
        for agent in self.signal_agents:
            weights[agent.__str__()] = random.uniform(0, 1)
        self.save_weights(weights)
        logging.info('Recalculated Weights')
        self.dao_agent.save_all_data()
        self.lock.release()

    def save_weights(self, weights):
        self.dao_agent.add_data(weights, Type.AGENT_WEIGHTS)