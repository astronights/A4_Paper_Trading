from .base_agent import BaseAgent
import time
import logging
import random
from config import constants
from utils.io_utils import Type

class BackTestingAgent(BaseAgent):

    def __init__(self, signal_agents, dao_agent):
        super().__init__()
        self.dao_agent = dao_agent
        self.signal_agents = signal_agents

    def run(self):
        while True:
            self.calculate()
            time.sleep(constants.CYCLE)

    def calculate(self):
        self.lock.acquire()
        account_book = self.dao_agent.account_book
        done_trades = None if account_book is None else account_book.loc[:account_book[account_book['Action'] == 'sell'].last_valid_index(),]
        if(done_trades is not None and len(done_trades) > 0):
            weights = self.dao_agent.agent_weights.iloc[-1].to_dict()
            new_weights = self._update_weights(weights, done_trades)
            self.save_weights(new_weights)
            self.update_cbr(done_trades)
            logging.info('Recalculated weights')
        else:
            logging.info('No weights to update')
        self.dao_agent.save_all_data()
        self.lock.release()

    def _update_weights(self, weights, done_trades):
        new_weights = weights
        trade_stack = []
        trade_value = 0.0
        for index, trade in done_trades:
            if trade['Action'] == 'buy':
                trade_stack.append(trade)
                trade_value = trade_value - float(trade['Quantity']*trade['Price'])
            elif trade['Action'] == 'sell':
                trade_value = trade_value + float(trade['Quantity']*trade['Price'])
                is_profit = -1 if trade_value < 0 else 1
                while(len(trade_stack) > 0):
                    buy_trade = trade_stack.pop()
                    for agent in self.signal_agents:
                        if(is_profit == 1):
                            new_weights[agent.__str__()] = new_weights[agent.__str__()] + (constants.LEARNING_RATE*buy_trade[agent.__str__()])
                        else:
                            new_weights[agent.__str__()] = new_weights[agent.__str__()] - (constants.LEARNING_RATE*buy_trade[agent.__str__()])
                for agent in self.signal_agents:
                    if(is_profit == 1):
                        new_weights[agent.__str__()] = new_weights[agent.__str__()] - (constants.LEARNING_RATE*trade[agent.__str__()])
                    else:
                        new_weights[agent.__str__()] = new_weights[agent.__str__()] + (constants.LEARNING_RATE*trade[agent.__str__()])
                trade_value = 0.0
        return new_weights

    def _save_weights(self, weights):
        self.dao_agent.add_data(weights, Type.AGENT_WEIGHTS)

    def update_cbr(self, account_book):
        #TODO update cbr
        pass