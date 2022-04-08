from agents.base_agent import BaseAgent
import time
import logging
from config import constants, signals
import numpy as np

class VARAgent(BaseAgent):

    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent
        self.alpha = signals.VAR_ALPHA
        self.data = []


    def run(self):
        while True:
            self.var()
            time.sleep(constants.TICK)

    def var(self):
        self.lock.acquire()
        df = self.broker_agent.ohlcv_data(constants.SYMBOL)
        price = df[constants.PRICE_COL].iloc[-1]
        periodic_ret = df[constants.PRICE_COL].pct_change().dropna().sort_values().reset_index(drop=True)
        xth = int(np.floor(self.alpha*len(periodic_ret))) - 1
        xth_smallest_rate = periodic_ret[max(xth, 0)]
        mean_return_rate = periodic_ret.mean()
        VaR = price * (mean_return_rate - xth_smallest_rate)
        self.data.append(VaR)
        self.updated = True
        logging.info(f'VaR Data updated {self.data[-1]}')
        self.lock.release()

    def get_latest_change(self):
        return 0 if len(self.data) < 2 else ((self.data[-1]/self.data[-2]) - 1.0)
