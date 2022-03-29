from agents.base_agent import BaseAgent
import time
from config import constants
from utils.io_utils import Type

class PNLAgent(BaseAgent):

    def __init__(self, broker_agent, dao_agent):
        super().__init__()
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent

    def run(self):
        while True:
            self.calculate()
            time.sleep(constants.TICK)

    def calculate(self):
        #TODO Check for open orders and act on them
        account_book = self.dao_agent.get_all_data(Type.ACCOUNT_BOOK)
