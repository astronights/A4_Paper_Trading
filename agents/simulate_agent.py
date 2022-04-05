import os
import math
import numpy as np
import pandas as pd
from config import constants
from utils import io_utils
from sklearn.linear_model import LogisticRegression

class SimulateAgent():

    def __init__(self, alpha=0.05):

        # Define agent names
        self.signal_agent_names = ['SentimentAgent', 'MAAgent', 'BollingerAgent', 'RSIAgent']
        self.macro_var = ['MACRO_0','MACRO_1','MACRO_2', 'VaR']

        # Load Historical Data
        self.data = pd.read_csv(os.path.join(constants.DATA_DIR, 'IS5006_Historical.csv'), index_col='datetime', parse_dates=[0], dayfirst=True)
        self.data['VaR'] = self.data['VaR'].pct_change()
        self.data['VaR'].fillna(0.0, inplace=True)
        
        # Initialise weights, CBR and equity portfolio
        self.agent_weights = [1.0/len(self.signal_agent_names)]*len(self.signal_agent_names)
        self.cbr = LogisticRegression(solver='liblinear')
        self.crypto = 0.0
        self.quantity = constants.QUANTITY
        self.capital = constants.START_CAPITAL
        self.alpha = alpha # learning rate
        self.pnl = []
        self.tradebook = pd.DataFrame(columns=['Action', 'Quantity', 'Price', 'Balance', 'PNL']+sorted(self.signal_agent_names)+self.macro_var)

    def simulate(self):
        for index, row in self.data.iterrows():
            dir = 0

            # Generate combined trade signal
            agent_signals = row[self.signal_agent_names].to_list()
            agent_signal = np.sum(np.dot(agent_signals, self.agent_weights))
            
            prev_rows = self.data[self.data.index < index]
            temp_capital = self.capital
            temp_crypto = self.crypto

            # Simulate trade based on signal
            if(agent_signal > 0):
                if(self.capital >= self.quantity*row['Close']):
                    self.data.loc[index, 'Action'] = 'buy'
                    self.data.loc[index, 'Quantity'] = self.quantity
                    self.data.loc[index, 'Price'] = row['Close']
                    temp_capital = self.capital - (self.quantity * row['Close'])
                    temp_crypto = self.crypto + self.quantity
                    self.data.loc[index, 'Balance'] = temp_capital
                    if(len(self.tradebook) > 20):
                        dir = self._run_cbr(self.data.loc[index])
                    ###### Reupdate quantity based on CBR ######
                    self.data.loc[index, 'Quantity'] = round((1.0-(float(dir)*constants.LEARNING_RATE))*self.quantity, 2)
                    temp_capital = self.capital - (self.data.loc[index, 'Quantity'] * row['Close'])
                    temp_crypto = self.crypto + self.data.loc[index, 'Quantity']
                    self.data.loc[index, 'Balance'] = temp_capital
                    ######################
                    self.capital = temp_capital
                    self.crypto = temp_crypto
                    self._update_tradebook(index, self.data.loc[index], prev_rows)
                else:
                    pass
            elif(agent_signal < 0):
                if(self.crypto > 0):
                    self.data.loc[index, 'Action'] = 'sell'
                    self.data.loc[index, 'Quantity'] = self.crypto
                    self.data.loc[index, 'Price'] = row['Close']
                    self.capital = self.capital + (self.crypto * row['Close'])
                    self.crypto = 0.0
                    self.data.loc[index, 'Balance'] = self.capital
                    self._evaluate(self.data.loc[index], prev_rows)
                    self._update_tradebook(index, self.data.loc[index], prev_rows)
                else:
                    pass
            else:
                continue
        print(f'Final PnL: {sum(self.pnl)}, Capital: {self.capital}, Crypto: {self.crypto} @ Price {self.data.iloc[-1]["Close"]}')
        print(f'Agent Weights: {self.agent_weights}')
        
        # Update final PnL for uncompleted trades (buys with no matching sell)
        for index, row in self.tradebook.iterrows():
            if(math.isnan(row['PNL'])):
                self.tradebook.loc[index:, 'PNL'] = (self.data.iloc[-1]["Close"] - row['Price'])*row['Quantity']
        self._save_data()

    def _evaluate(self, sell_row, prev_rows):
        # Calculate average buy price, buy quantity, sell price, sell quantity and PnL
        buy_rows = prev_rows[prev_rows['Action'] == 'buy'].iloc[-int(round(sell_row['Quantity'])):]
        buy_quantity = buy_rows['Quantity'].sum()
        buy_price = (buy_rows['Price']*buy_rows['Quantity']).sum()/buy_quantity
        pnl = (sell_row['Price']*sell_row['Quantity']) - (buy_price*buy_quantity)
        self.pnl.append(pnl)
        print(f'Capital: {self.capital} PnL: {pnl}; selling {sell_row["Quantity"]} @ {sell_row["Price"]} & buying {buy_quantity} @ {buy_price}')
        
        # Update weights depending on whether profit or loss for given trades
        if(pnl < 0):
            sell_signals = sell_row[self.signal_agent_names].to_list()
            buy_signals = buy_rows[self.signal_agent_names].sum().to_list()
            self.agent_weights = np.add(self.agent_weights, np.subtract(self._scalar_mult(sell_signals), self._scalar_mult(buy_signals)))
        elif(pnl > 0):
            sell_signals = sell_row[self.signal_agent_names].to_list()
            buy_signals = buy_rows[self.signal_agent_names].sum().to_list()
            self.agent_weights = np.subtract(self.agent_weights, np.subtract(self._scalar_mult(sell_signals), self._scalar_mult(buy_signals)))

    def _scalar_mult(self, signals):
        # Function to help scalar list multiplication
        return([x*self.alpha for x in signals])

    def _update_tradebook(self, index, row, prev_rows):
        # Update data in tradebook along with PnL for closed trades
        if(row['Action'] == 'buy'):
            self.tradebook.loc[index] = [row['Action'], row['Quantity'], row['Price'], row['Balance'], np.NaN] + row[self.signal_agent_names].to_list() + row[self.macro_var].to_list()
        else:
            buy_rows = prev_rows[prev_rows['Action'] == 'buy'].iloc[-int(round(row['Quantity'])):]
            buy_quantity = buy_rows['Quantity'].sum()
            buy_price = (buy_rows['Price']*buy_rows['Quantity']).sum()/buy_quantity
            pnl = (row['Price']*row['Quantity']) - (buy_price*buy_quantity)
            for ix in buy_rows.index.to_list():
                self.tradebook.loc[ix, 'PNL'] = pnl
            self.tradebook.loc[index] = [row['Action'], row['Quantity'], row['Price'], row['Balance'], pnl] + row[self.signal_agent_names].to_list() + row[self.macro_var].to_list()

    def _save_data(self):
        # Save weights, tradebook and CBR model to csv
        io_utils.df_to_csv(self.tradebook, os.path.join(constants.DATA_DIR, 'tradebook.csv'))
        io_utils.save_pickle(self.cbr, os.path.join(constants.DATA_DIR, 'cbr.pkl'))
        agent_weights_df = pd.DataFrame(columns=self.signal_agent_names)
        agent_weights_df.loc[0] = self.agent_weights
        io_utils.df_to_csv(agent_weights_df, os.path.join(constants.DATA_DIR, 'agent_weights.csv'))

    def _run_cbr(self, row):
        # Run CBR model to get direction
        last_non_nan = self.tradebook['PNL'].last_valid_index()
        X, y = self.tradebook.loc[:last_non_nan, self.tradebook.columns != 'PNL'].copy(), self.tradebook.loc[:last_non_nan, 'PNL'].copy()
        X.loc[:, 'Action'] = X['Action'].apply(lambda x: 1 if 'buy' else -1)
        y = np.where(y > 0, 1, -1)
        self.cbr.fit(X, y)
        pred_row = pd.DataFrame(row).T
        pred_row.loc[:, 'Action'] = pred_row['Action'].apply(lambda x: 1 if 'buy' else -1)
        pred_row.drop(['Open', 'High', 'Low', 'Close', 'Volume'], inplace = True, axis=1)
        pred_pnl = self.cbr.predict(pred_row)
        return(pred_pnl[0])