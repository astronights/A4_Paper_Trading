from agents.base_agent import BaseAgent
import time
import logging
from config import constants
import numpy as np

class VARAgent(BaseAgent):

    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent
        self.alpha = 0.01
        self.data = None


    def run(self):
        while True:
            self.var()
            time.sleep(constants.TICK)

    def var(self):
        self.lock.acquire()
        data = self.broker_agent.ohlcv_data(constants.SYMBOL)
        price = data[constants.PRICE_COL].iloc[-1]
        periodic_ret = data[constants.PRICE_COL].pct_change().dropna().sort_values().reset_index(drop=True)
        xth = int(np.floor(0.01*len(periodic_ret))) - 1
        xth_smallest_rate = periodic_ret[xth]
        mean_return_rate = periodic_ret.mean()
        VaR = price * (mean_return_rate - xth_smallest_rate)
        self.data = VaR
        self.updated = True
        logging.info('VaR Data updated')
        self.lock.release()
