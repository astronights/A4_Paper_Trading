from .base_agent import BaseAgent
from config import constants
import time
from datetime import datetime
import logging
import random
import pandas as pd
from utils import io_utils

class DeciderAgent(BaseAgent):

    def __init__(self, signal_agents, broker_agent, macroecon_agent, var_agent, dao_agent, ceo_agent):
        super().__init__()
        self.signal_agents = signal_agents
        self.broker_agent = broker_agent
        self.macroecon_agent = macroecon_agent
        self.var_agent = var_agent
        self.dao_agent = dao_agent
        self.ceo_agent = ceo_agent
        self.trade = {}
        self.cbr_columns = ['Action', 'Quantity', 'Price', 'Balance']+sorted([x.__str__() for x in self.signal_agents])+['MACRO_0', 'MACRO_1', 'MACRO_2', 'VaR']
        
    def run(self):
        while True:
            # Verify if all signal agents have generated a signal
            updated_signals = all([agent.updated for agent in (self.signal_agents+[self.macroecon_agent, self.var_agent])])
            if(updated_signals):
                self.decide()
                time.sleep(constants.TICK)
            else:
                continue

    def decide(self):
        self.lock.acquire()
        self.trade = {}
        prev_balance = self.broker_agent.get_balance('cash')
        
        # Compute Final Trade Direction based on agent signals and agent weights
        weights = self.dao_agent.get_last_data(io_utils.Type.AGENT_WEIGHTS).to_dict()
        latest_actions = dict([(agent.__str__(), agent.latest()) for agent in self.signal_agents])
        # latest_actions = dict([(agent.__str__(), float(random.randint(-1, 1))) for agent in self.signal_agents])
        action = sum([weights[agent_name] * latest_actions[agent_name] for agent_name in weights.keys()])
        logging.info(f'Agent Signals: {latest_actions}')

        # Populate signals, macroeconomic data and trade decision to object
        for agent_action in latest_actions.keys():
            self.trade[agent_action] = latest_actions[agent_action]
        for macro_val in self.macroecon_agent.get_data_as_dict().keys():
            self.trade[macro_val] = self.macroecon_agent.get_data_as_dict()[macro_val]
        self.trade['VaR'] = self.var_agent.get_latest_change()
        self.trade['Action'] = 'buy' if action > 0.25 else ('sell' if action < -0.25 else 'none')
        self.trade['Price'] = self.broker_agent.latest_ohlcv(constants.SYMBOL)[constants.PRICE_COL]
        self.trade['Type'] = 'market'
        self.trade['Quantity'] = constants.QUANTITY
        self.trade['Balance'] = prev_balance + (1 if action > 0.25 else (-1 if action < -0.25 else 0)) * self.trade['Quantity'] * self.trade['Price']
        self.trade['Quantity'] = self._update_with_cbr(self.trade)

        str_price = 'market price' if self.trade['Type'] == 'market' else str(self.trade['Price'])
        logging.info(f'{self.trade["Action"].title()} Trade Decided @ {str_price}')

        # Send trade to CEO agent for evaluation and summarize metrics
        self.trade = self.ceo_agent.make_trade(self.trade)
        self.trade['Total_Balance'] = self.trade['Balance'] + (self.broker_agent.get_balance(constants.SYMBOL) * self.trade[constants.PRICE_COL])
        self.trade['Timestamp'] = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
        self.trade['Crypto'] = self.broker_agent.get_balance(constants.SYMBOL)
        logging.info(f'{self.trade}')

        # Reset signal agent flags
        for agent in (self.signal_agents+[self.var_agent]):
            agent.updated = False
        self.updated = True
        self.lock.release()
        
    def _update_with_cbr(self, trade):
        # Calculate trade quantity based on CBR model
        # Decide quantity on buy trades using CBR and liquidate all crypto on sell trades
        if(trade['Action'] == 'buy'):
            cbr_model = self.dao_agent.cbr_model
            cbr_trade = pd.DataFrame(trade, index=[0])
            cbr_trade.drop(['Type'], axis=1, inplace=True)
            cbr_trade.loc[0, 'Price'] = self.broker_agent.latest_ohlcv(constants.SYMBOL)[constants.PRICE_COL]
            cbr_trade.loc[:, 'Action'] = cbr_trade['Action'].apply(lambda x: 1 if 'buy' else (-1 if 'sell' else 0))
            cbr_trade = cbr_trade[self.cbr_columns]
            dir = cbr_model.predict(cbr_trade)[0]
            return(1.0-(float(dir)*constants.LEARNING_RATE/2))*constants.QUANTITY
        elif(trade['Action'] == 'sell'):
            return self.broker_agent.get_balance(constants.SYMBOL)
        return(constants.QUANTITY)
