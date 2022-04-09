from agents.base_agent import BaseAgent
import time
import logging
from config import constants, signals
import numpy as np

"""VARAgent o calculate Value at Risk (VaR) for trading asset"""
class VARAgent(BaseAgent):

    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent

        # Initialise alpha from config
        self.alpha = signals.VAR_ALPHA
        self.data = []


    """Run on every tick to calculate VaR value"""
    def run(self):
        while True:
            self.var()
            time.sleep(constants.TICK)

    """ Calculate non paramteric VaR value using formulae"""
    def var(self):
        self.lock.acquire()

        # Get historic OHLCV data
        df = self.broker_agent.ohlcv_data(constants.SYMBOL)
        price = df[constants.PRICE_COL].iloc[-1]

        # Calculate periodic returns
        periodic_ret = df[constants.PRICE_COL].pct_change().dropna().sort_values().reset_index(drop=True)
        xth = int(np.floor(self.alpha*len(periodic_ret))) - 1
        
        # Return 0 if non enoguh candlesticks returned from BrokerAgent
        xth_smallest_rate = periodic_ret[max(xth, 0)]
        mean_return_rate = periodic_ret.mean()

        # Calculate VaR
        VaR = price * (mean_return_rate - xth_smallest_rate)
        self.data.append(VaR)
        self.updated = True
        logging.info(f'VaR Data updated {self.data[-1]}')
        self.lock.release()

    """
    Calculate latest percentage change in VaR
    Return 0 if not enough values to calculate
    """
    def get_latest_change(self):
        return 0 if len(self.data) < 2 else ((self.data[-1]/self.data[-2]) - 1.0)
