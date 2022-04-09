import os
import time
import logging
from .base_agent import BaseAgent
from config import constants, fred
from utils import io_utils
import pandas as pd
from fredapi import Fred

"""MacroeconomicAgent to get MacroEconomic data from FRED API"""
class MacroEconAgent(BaseAgent):
    
    def __init__(self):
        super().__init__()

        # Connect to FRED using API credentials from config
        self.fred = Fred(api_key=fred.FRED_API)

        # Load PCA model from simulation
        self.pca = io_utils.load_pickle(os.path.join(constants.DATA_DIR, 'macro_pca.pkl'))
        self.pca_cols = [f'MACRO_{i}' for i in range(self.pca.n_components)]
        self.macro_series = {'inflation': 'FPCPITOTLZGUSA', 'unemployment': 'UNRATE', 
        'oil': 'DCOILWTICO', 'gold_vix': 'GVZCLS', 'cboe_vix':'VIXCLS', 'dow_jones': 'DJIA',
        'interest_rate': 'IR3TIB01USM156N'}
        self.data = None

    """Update macroeconomic signal on every cycle"""
    def run(self):
        while True:
            self.macro_data()
            time.sleep(constants.CYCLE)

    """
    Generate macro-economic signals
    Pass through PCA model
    """
    def macro_data(self):
        self.lock.acquire()
        temp_df = pd.DataFrame(index=[0])
        
        # Get data from FRED API
        for key in self.macro_series.keys():
            df = self.fred.get_series(self.macro_series[key])
            temp_df.at[0, key] = df.iloc[-1]

        # Transform with PCA
        self.data = pd.DataFrame(self.pca.transform(temp_df), columns = self.pca_cols, index=[0])
        self.updated = True
        logging.info('Macro Data updated')
        self.lock.release()

    """ Return latest macro-economic signals as dictionary instead of dataframe row"""
    def get_data_as_dict(self):
        return self.data.iloc[-1].to_dict() if self.data is not None else {}
        