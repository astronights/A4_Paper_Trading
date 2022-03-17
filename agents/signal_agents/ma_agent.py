import time
import logging
import numpy as np
from .base_agent import BaseAgent
from threading import Thread
from config import constants
from config.constants import *

class MAAgent(BaseAgent):
    
        def __init__(self, broker_agent):
            super().__init__()
            self.broker_agent = broker_agent
    
        def run(self):
            while True:
                self.signal()
                time.sleep(constants.TICK)
    
        def signal(self):
            self.lock.acquire()
            df = self.broker_agent.ohlcv_data(SYMBOL)
            df['EMA_10'] = df[self.broker_agent.price_col].ewm(span=10, adjust = False).mean()
            df['SMA_50'] = df[self.broker_agent.price_col].rolling(50).mean()
            df[f'MA_Position'] = np.where(df[f'EMA_10'] > df[f'SMA_50'], 1.0, 0.0)
            df[f'MA_Signal'] = df[f'MA_Position'].diff()
            df.drop([f'MA_Position'], axis=1, inplace=True)
            self.signals.append(df.iloc[-1][f'MA_Signal'])
            self.lock.release()