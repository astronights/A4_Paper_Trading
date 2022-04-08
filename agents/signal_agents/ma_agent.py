import time
import logging
import numpy as np
from .base_signal_agent import BaseSignalAgent
from config import constants, signals

class MAAgent(BaseSignalAgent):
    
    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent

    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)

    def signal(self):
        self.lock.acquire()
        df = self.broker_agent.ohlcv_data(constants.SYMBOL)
        df['EMA'] = df[constants.PRICE_COL].ewm(span=signals.EMA, adjust = False).mean()
        df['SMA'] = df[constants.PRICE_COL].rolling(signals.SMA).mean()
        df[f'MA_Position'] = np.where(df[f'EMA'] > df[f'SMA'], 1.0, 0.0)
        df[f'MA_Signal'] = df[f'MA_Position'].diff()
        df.drop([f'MA_Position'], axis=1, inplace=True)
        self.signals.append(df.iloc[-1][f'MA_Signal'])
        self.updated = True
        logging.info(f'MA Signal: {self.signals[-1]}')
        self.lock.release() 