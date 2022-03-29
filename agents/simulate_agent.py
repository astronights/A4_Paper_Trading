import os
import numpy as np
import pandas as pd
from config import constants
from sklearn.neighbors import KNeighborsClassifier

class SimulateAgent():

    def __init__(self, alpha=0.05):
        self.data = pd.read_csv(os.path.join(constants.DATA_DIR, 'IS5006_Historical.csv'), index_col='datetime', parse_dates=[0], dayfirst=True)
        self.signal_agent_names = ['Fuzzy_sentiment_signal', 'MA_Signal', 'Bollinger']
        self.macro_var = ['MACRO_0','MACRO_1','MACRO_2', 'VaR']
        self.agent_weights = [1.0/len(self.signal_agent_names)]*len(self.signal_agent_names)
        self.macro_var_weights = [1.0/len(self.macro_var)]*len(self.macro_var)
        self.knn = KNeighborsClassifier(n_neighbors=3)
        self.crypto = 0.0
        self.quantity = constants.QUANTITY
        self.capital = constants.START_CAPITAL
        self.alpha = alpha # learning rate
        self.pnl = []

    def simulate(self):
        for index, row in self.data.iterrows():
            agent_signals = row[self.signal_agent_names].to_list()
            agent_signal = np.sum(np.dot(agent_signals, self.agent_weights))
            prev_rows = self.data[self.data.index < index]
            macro_var_signals = self.get_macro_var_signal(row, prev_rows)
            if(agent_signal > 0):
                print(f'Macro signal: {macro_var_signals} @ buy {self.quantity} BTC {row["Close"]}')
                if(self.capital >= self.quantity*row['Close']):
                    self.data.loc[index, 'Action'] = 'buy'
                    self.data.loc[index, 'Quantity'] = self.quantity
                    self.data.loc[index, 'Price'] = row['Close']
                    self.data.loc[index, 'Type'] = 'market'
                    self.capital = self.capital - (self.quantity * row['Close'])
                    self.crypto = self.crypto + self.quantity
                    self.data.loc[index, 'Balance'] = self.capital
                else:
                    pass
            elif(agent_signal < 0):
                print(f'Macro signal: {macro_var_signals} @ sell {self.crypto} BTC, {row["Close"]}')
                if(self.crypto > 0):
                    self.data.loc[index, 'Action'] = 'sell'
                    self.data.loc[index, 'Quantity'] = self.crypto
                    self.data.loc[index, 'Price'] = row['Close']
                    self.data.loc[index, 'Type'] = 'market'
                    self.capital = self.capital + (self.crypto * row['Close'])
                    self.crypto = 0.0
                    self.data.loc[index, 'Balance'] = self.capital
                    self.evaluate(self.data.loc[index], prev_rows)
                else:
                    pass
            else:
                continue
        print(f'Final PnL: {sum(self.pnl)}, Capital: {self.capital}, Crypto: {self.crypto}')
        print(f'Agent Weights: {self.agent_weights}')

    def evaluate(self, sell_row, prev_rows):
        buy_rows = prev_rows[prev_rows['Action'] == 'buy'].iloc[-int(sell_row['Quantity']):]
        buy_quantity = buy_rows['Quantity'].sum()
        buy_price = buy_rows['Price'].sum()/buy_quantity
        pnl = (sell_row['Price']*sell_row['Quantity']) - (buy_price*buy_quantity)
        self.pnl.append(pnl)
        print(f'Capital: {self.capital} PnL: {pnl} @ selling {sell_row["Price"]} @ buying {buy_price}')
        if(pnl < 0):
            sell_signals = sell_row[self.signal_agent_names].to_list()
            buy_signals = buy_rows[self.signal_agent_names].sum().to_list()
            self.agent_weights = np.add(self.agent_weights, np.subtract(self._scalar_mult(sell_signals), self._scalar_mult(buy_signals)))
        elif(pnl > 0):
            sell_signals = sell_row[self.signal_agent_names].to_list()
            buy_signals = buy_rows[self.signal_agent_names].sum().to_list()
            self.agent_weights = np.subtract(self.agent_weights, np.subtract(self._scalar_mult(sell_signals), self._scalar_mult(buy_signals)))

    def _scalar_mult(self, signals):
        return([x*self.alpha for x in signals])

    def get_macro_var_signal(self, cur_row, prev_rows):
        if((len(prev_rows) == 0) or ('Action' not in prev_rows.columns)):
            return(-1.0)
        prev_trade_row = prev_rows[~prev_rows['Action'].isnull()].iloc[-1]
        macro_var_pct = np.divide(cur_row[self.macro_var].to_list(), prev_trade_row[self.macro_var].to_list()) - 1.0
        macro_var_signal = np.sum(np.dot(macro_var_pct, self.macro_var_weights))
        return(macro_var_signal)