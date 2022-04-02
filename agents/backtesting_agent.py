from .base_agent import BaseAgent
import time
import logging
import random
from config import constants
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from utils.io_utils import Type

class BackTestingAgent(BaseAgent):

    def __init__(self, signal_agents, dao_agent):
        super().__init__()
        self.dao_agent = dao_agent
        self.signal_agents = signal_agents
        self.cbr_columns = ['Action', 'Quantity', 'Price', 'Balance']+sorted([x.__str__() for x in self.signal_agents])+['MACRO_0', 'MACRO_1', 'MACRO_2', 'VaR']

    def run(self):
        while True:
            self.calculate()
            time.sleep(constants.CYCLE)

    def calculate(self):
        self.lock.acquire()
        account_book = self.dao_agent.account_book
        if(account_book is not None and 'PNL' in account_book.columns and account_book['PNL'].notna().any()):
            weights = self.dao_agent.agent_weights.iloc[-1].to_dict()
            done_trades = account_book[~account_book['PNL'].isnull()]
            new_weights = self._update_weights(weights, done_trades)
            self._save_weights(new_weights)
            self.update_cbr(done_trades)
            self.dao_agent.save_all_data()
            logging.info('Recalculated weights and CBR')
        else:
            logging.info('No completed trades to update')
        self.lock.release()

    def _update_weights(self, weights, done_trades):
        new_weights = weights.copy()
        for index, trade in done_trades.iterrows():
            is_profit = -1 if trade['PNL'] < 0 else 1
            if trade['Action'] == 'buy':
                for agent in self.signal_agents:
                    if(is_profit == 1):
                        new_weights[agent.__str__()] = new_weights[agent.__str__()] + (constants.LEARNING_RATE*trade[agent.__str__()])
                    else:
                        new_weights[agent.__str__()] = new_weights[agent.__str__()] - (constants.LEARNING_RATE*trade[agent.__str__()])
            elif trade['Action'] == 'sell':
                for agent in self.signal_agents:
                    if(is_profit == 1):
                        new_weights[agent.__str__()] = new_weights[agent.__str__()] - (constants.LEARNING_RATE*trade[agent.__str__()])
                    else:
                        new_weights[agent.__str__()] = new_weights[agent.__str__()] + (constants.LEARNING_RATE*trade[agent.__str__()])
        return new_weights

    def _save_weights(self, weights):
        self.dao_agent.add_data(weights, Type.AGENT_WEIGHTS)

    def update_cbr(self, account_book):
        historic_trades = self.dao_agent.get_historic_tradebook()
        old_account_book = self.dao_agent.load_all_data(Type.ACCOUNT_BOOK)
        old_trades = None if old_account_book is None else old_account_book[self.cbr_columns+['PNL']]
        new_trades = account_book[self.cbr_columns+['PNL']]
        updated_trades = pd.concat([historic_trades, old_trades, new_trades], axis=0)
        cbr = LogisticRegression(solver='liblinear')
        X, y = updated_trades.loc[:, updated_trades.columns != 'PNL'].copy(), updated_trades.loc[:, 'PNL'].copy()
        X.loc[:, 'Action'] = X['Action'].apply(lambda x: 1 if 'buy' else -1)
        y = np.where(y > 0, 1, -1)
        cbr.fit(X, y)
        self.dao_agent.cbr_model = cbr