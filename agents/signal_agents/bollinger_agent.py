import time
import logging
import numpy as np
from .base_signal_agent import BaseSignalAgent
from config import constants, signals

""" BollingerAgent class inherited from BaseSignalAgent """
class BollingerAgent(BaseSignalAgent):
    
    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent
    
    """ Generate signal on every tick """
    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)
    
    """
    Calculated SMA over 20 time periods.
    The top band(HIGH_band_20) is two standard deviations above the SMA.
    The bottom band(LOW_Band_20) is two standard deviations below the SMA. 
    The stock's closing prices generally stay near the middle of both Bollinger bands. 
    When the price line hits the lower band, a buy signal is generated.
    When the price line hits the higher band, a sell signal is generated.
    """
    def signal(self):
        self.lock.acquire()
        df = self.broker_agent.ohlcv_data(constants.SYMBOL,constants.TIMEFRAME)
        df['SMA'] = df[constants.PRICE_COL].rolling(signals.BOLLINGER).mean()
        df['STD'] = df[constants.PRICE_COL].rolling(signals.BOLLINGER).std()
        df['LOW_Band'] = df['SMA'] - df['STD'] * 2
        df['HIGH_Band'] = df['SMA'] + df['STD'] * 2
        df['Sell_Signal'] = np.where(df[constants.PRICE_COL] >= df['HIGH_Band'], 1, 0)
        df['Sell_Position'] = df['Sell_Signal'].diff()
        df['Buy_Signal'] = np.where(df[constants.PRICE_COL] <= df['LOW_Band'], 1, 0)
        df['Buy_Position'] = df['Buy_Signal'].diff()
        if df.iloc[-1]['Buy_Position']==1:
            self.signals.append(1.0)
        elif df.iloc[-1]['Sell_Position']==1:
            self.signals.append(-1.0)
        else:
            self.signals.append(0.0)
        self.updated = True
        logging.info(f'Bollinger Signal: {self.signals[-1]}')
        self.lock.release()
        
    