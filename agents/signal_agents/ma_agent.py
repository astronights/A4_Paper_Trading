import time
import logging
import numpy as np
from .base_signal_agent import BaseSignalAgent
from config import constants, signals

""" MAAgent class inherited from BaseSignalAgent """
class MAAgent(BaseSignalAgent):
    
    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent

    """ Generate signal on every tick """
    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)
    
    """
    Calculated SMA over 50 days(long) and EMA over 10 days(short)
    Generate singnal 1 if 10 days EMA(short term or faster MA) is greater than 50 days SMA(long term or slower MA), else 0.    
    Create a new column Position to store day-to-day difference of the Signal column. 
    Position= 1,  Signal has changed from 0 to 1, (EMA_10) has crossed above SMA_50, a buy signal is generated
    Position= -1, Signal has changed from 1 to 0, (EMA_10) has crossed below SMA_50, a sell signal is generated
    """
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