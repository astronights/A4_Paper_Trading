import time
import logging
import numpy as np
from .base_signal_agent import BaseSignalAgent
from config import constants, signals

""" RSIAgent class inherited from BaseSignalAgent """
class RSIAgent(BaseSignalAgent):
    
    def __init__(self, broker_agent):
        super().__init__()
        self.broker_agent = broker_agent

    """ Generate signal on every tick """
    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)

    """
    Calculate RSI over the RSI_AVERAGE timeframe based on the average closes on green time periods and red time periods
    Calculate current sell signal to be 1 if RSI is greater or equal to RSI_OVERBOUGHT level, else 0.    
    Calculate current buy signal to be 1 if RSI is less than or equal to RSI_OVERSOLD level, else 0.   
    Create a new column RSI_Sell_Position and RSI_Buy_Position to store the row-to-row difference in the Sell and Buy Signal columns respectively. 
    Generate and return signal -1 if a new sell signal has been calculated or 1 if a new buy signal has been calculated, else 0
    """

    def signal(self):
        self.lock.acquire()
        df = self.broker_agent.ohlcv_data(constants.SYMBOL,constants.TIMEFRAME)

        #Calculate 14 day RSI value, ranges betweeen 0 to 100
        df['diff'] = df[constants.PRICE_COL].diff(1)
        df['gain'] = df['diff'].clip(lower=0).round(2)
        df['loss'] = df['diff'].clip(upper=0).round(2)
        df['avg_gain'] = df['gain'].rolling(signals.RSI_AVERAGE).mean()
        df['avg_loss'] = -df['loss'].rolling(signals.RSI_AVERAGE).mean()
        df['rs'] = df['avg_gain'] / df['avg_loss']
        df['rsi'] = 100 - (100/(1.0 + df['rs']))

        df['RSI_Sell_Signal'] = np.where(df['rsi'] >= signals.RSI_OVERBOUGHT, 1, 0)
        df['RSI_Buy_Signal'] = np.where(df['rsi'] <= signals.RSI_OVERSOLD, 1, 0)
        df['RSI_Sell_Position'] = df['RSI_Sell_Signal'].diff()
        df['RSI_Buy_Position'] = df['RSI_Buy_Signal'].diff()
        if df.iloc[-1]['RSI_Buy_Position']==1:
            self.signals.append(1.0)
        elif df.iloc[-1]['RSI_Sell_Position']==1:
            self.signals.append(-1.0)
        else:
            self.signals.append(0.0)
        self.updated = True
        logging.info(f'RSI Signal: {self.signals[-1]}')
        self.lock.release()
        