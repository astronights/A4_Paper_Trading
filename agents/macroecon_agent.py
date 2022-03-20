import time
import logging
from .base_agent import BaseAgent
from config import constants, fred
from fredapi import Fred

class MacroEconAgent(BaseAgent):
    
    def __init__(self):
        super().__init__()
        self.fred = Fred(api_key=fred.FRED_API)
        self.macro_series = {'inflation': 'FPCPITOTLZGUSA', 'unemployment': 'UNRATE', 
        'oil': 'DCOILWTICO', 'gold_vol': 'GVZCLS'}
        self.data = {}

    def run(self):
        while True:
            self.macro_data()
            time.sleep(constants.TICK)

    def macro_data(self):
        self.lock.acquire()
        for key in self.macro_series.keys():
            df = self.fred.get_series(self.macro_series[key])
            self.data[key] = df.iloc[-1]
        self.lock.release()
        logging.info(f'Macro Data: {self.data}')

    def get_data(self):
        return self.data