from .base_agent import BaseAgent
from config import constants
import os
import time
import logging
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
        
    def run(self):
        while True:
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
        #TODO: Calculate action and quantity using some CBR
        weights = self.dao_agent.get_last_data(io_utils.Type.AGENT_WEIGHTS).to_dict()
        latest_actions = dict([(agent.__str__(), agent.latest()) for agent in self.signal_agents])
        logging.info(f'Agent Signals: {latest_actions}')
        for agent_action in latest_actions.keys():
            self.trade[agent_action] = latest_actions[agent_action]
        for macro_val in self.macroecon_agent.get_data_as_dict().keys():
            self.trade[macro_val] = self.macroecon_agent.get_data_as_dict()[macro_val]
        self.trade['VaR'] = self.var_agent.get_latest_change()
        action = sum([weights[agent_name] * latest_actions[agent_name] for agent_name in weights.keys()])
        self.trade['Action'] = 'buy' if action > 0.25 else ('sell' if action < -0.25 else 'none')
        self.trade['Price'] = None
        self.trade['Type'] = 'market'
        self.trade['Quantity'] = self._update_with_cbr(self.trade)
        str_price = 'market price' if self.trade['Type'] == 'market' else str(self.trade['Price'])
        logging.info(f'{self.trade["Action"].title()} Trade Decided @ {str_price}')
        self.trade = self.ceo_agent.make_trade(self.trade)
        self.trade['Total_Balance'] = self.trade['Cash_Balance'] + (self.broker_agent.get_balance(constants.SYMBOL) * self.trade[constants.PRICE_COL])
        for agent in (self.signal_agents+[self.var_agent]):
            agent.updated = False
        self.updated = True
        self.lock.release()
        
    def _update_with_cbr(self, trade):
        if(trade['Action'] == 'buy'):
            cbr_model = self.dao_agent.cbr_model
            dir = cbr_model.predict(trade)[0]
            return(1.0-(float(dir)*constants.LEARNING_RATE/2))*constants.QUANTITY
        elif(trade['Action'] == 'sell'):
            return self.broker_agent.get_balance(constants.SYMBOL)
        return(constants.QUANTITY)
