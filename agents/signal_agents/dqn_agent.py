import time
import logging
import numpy as np
from .base_signal_agent import BaseSignalAgent
from threading import Thread
from config import constants
from config.constants import *

class DQNAgent(BaseSignalAgent):
    
    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent

    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)

    def signal(self):
        self.lock.acquire()
        df = self.broker_agent.ohlcv_data(SYMBOL,TIMEFRAME)
        df['SMA_20'] = df[constants.PRICE_COL].rolling(20).mean()
        df['STD_20'] = df[constants.PRICE_COL].rolling(20).std()
        df['LOW_Band_20'] = df['SMA_20'] - df['STD_20'] * 2
        df['HIGH_Band_20'] = df['SMA_20'] + df['STD_20'] * 2
        df['Sell_Signal'] = np.where(df[constants.PRICE_COL] >= df['HIGH_Band_20'], 1, 0)
        df['Sell_Position'] = df['Sell_Signal'].diff()
        df['Buy_Signal'] = np.where(df[constants.PRICE_COL] <= df['LOW_Band_20'], 1, 0)
        df['Buy_Position'] = df['Buy_Signal'].diff()
        

        if df.iloc[-1]['Buy_Position']==-1:
            self.signals.append(1)
        elif df.iloc[-1]['Sell_Position']==-1:
            self.signals.append(-1)
        else:
            self.signals.append(0)
        self.lock.release()
        logging.info(f'DQN Signal: {self.signals[-1]}')
        
    