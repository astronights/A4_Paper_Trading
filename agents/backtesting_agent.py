from .base_agent import BaseAgent
import time
import logging
import random
from config import constants
from data_io import csv_io

class BackTestingAgent(BaseAgent):

    def __init__(self, account_agent, signal_agents):
        super().__init__()
        self.account_agent = account_agent
        self.signal_agents = signal_agents

    def run(self):
        while True:
            self.calculate()
            time.sleep(constants.CYCLE)

    def calculate(self):
        self.lock.acquire()
        account_book = self.account_agent.load_from_file()
        #TODO: Calculate Weights using some algorithm
        weights = {}
        for agent in self.signal_agents:
            weights[agent.__str__()] = random.uniform(0, 1)
        self.save_weights(weights)
        logging.info('Recalculated Weights')
        self.lock.release()

    def save_weights(self, weights):
        csv_io.save_data(weights, csv_io.Type.AGENT_WEIGHTS)