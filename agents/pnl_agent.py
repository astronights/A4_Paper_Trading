from agents.base_agent import BaseAgent
import time
from config import constants
from utils.io_utils import Type
import logging

class PNLAgent(BaseAgent):

    def __init__(self, broker_agent, dao_agent):
        super().__init__()
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent

    def run(self):
        while True:
            self.calculate()
            time.sleep(constants.CYCLE)

    def calculate(self):
        #TODO How to calculate PnL on every order?
        account_book = self.dao_agent.account_book
        cur_order_ids = account_book['Client_order_id'].to_list() if(account_book is not None) else []
        orders = self.broker_agent.orders()
        pnl = 0.0
        for order in orders:
            order_raw = order._raw
            if(order_raw['client_order_id'] in cur_order_ids):
                if(order_raw['status'] == 'accepted'):
                    self.broker_agent.cancel_order(order_raw['id'])
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Status'] = 'cancelled'
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Updated_at'] = order_raw['updated_at']
                else:
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Status'] = order_raw['status']
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Updated_at'] = order_raw['updated_at']
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Price'] = float(order_raw['filled_avg_price'])
                    if(order_raw['side'] == 'buy'):
                        pnl = pnl - float(order_raw['qty'])*float(order_raw['filled_avg_price'])
                    else:
                        pnl = pnl + float(order_raw['qty'])*float(order_raw['filled_avg_price'])
                        account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'PNL'] = pnl
                        pnl = 0
                logging.info(f'Updated order {order_raw["client_order_id"]}')
        self.dao_agent.add_full_df(account_book, Type.ACCOUNT_BOOK)
