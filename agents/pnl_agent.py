from agents.base_agent import BaseAgent
import time
import sys
from config import constants
from utils.io_utils import Type
import logging

class PNLAgent(BaseAgent):

    def __init__(self, broker_agent, dao_agent, backtesting_agent):
        super().__init__()
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent
        self.backtesting_agent = backtesting_agent

    def run(self):
        while True:
            self.calculate()
            self.backtesting_agent.calculate()
            time.sleep(constants.CYCLE)

    def stop_trade(self):
        self.dao_agent.save_all_data()
        sys.exit(0)

    def calculate(self):
        #TODO How to calculate PnL on every order?
        account_book = self.dao_agent.account_book
        cur_order_ids = account_book['Client_order_id'].to_list() if(account_book is not None) else []
        orders = sorted(self.broker_agent.orders(), key = lambda order: order._raw['updated_at'])
        buy_stack = []
        pnl = 0.0
        for order in orders:
            order_raw = order._raw
            if(order_raw['client_order_id'] in cur_order_ids):
                logging.info(order_raw['updated_at'])
                if(order_raw['status'] == 'accepted'):
                    self.broker_agent.cancel_order(order_raw['id'])
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Status'] = 'cancelled'
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Updated_at'] = order_raw['updated_at']
                elif(order_raw['status'] == 'filled'):
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Status'] = order_raw['status']
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Updated_at'] = order_raw['updated_at']
                    account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'Price'] = float(order_raw['filled_avg_price'])
                    if(order_raw['side'] == 'buy'):
                        pnl = pnl - float(order_raw['qty'])*float(order_raw['filled_avg_price'])
                        buy_stack.append(order_raw['client_order_id'])
                    else:
                        pnl = pnl + float(order_raw['qty'])*float(order_raw['filled_avg_price'])
                        for c in buy_stack:
                            account_book.loc[account_book['Client_order_id']==c, 'PNL'] = pnl
                        account_book.loc[account_book['Client_order_id']==order_raw['client_order_id'], 'PNL'] = pnl
                        buy_stack = []
                        pnl = 0.0
                logging.info(f'Updated order {order_raw["client_order_id"]}')
        self.dao_agent.add_full_df(account_book, Type.ACCOUNT_BOOK)
        final_balance = self.broker_agent.get_balance('cash') + (self.broker_agent.get_balance(constants.SYMBOL)*self.broker_agent.latest_ohlcv(constants.SYMBOL)[constants.PRICE_COL])
        logging.info(f'{self.broker_agent.get_balance("cash")}, {self.broker_agent.get_balance(constants.SYMBOL)}')
        if((final_balance >= self.broker_agent.start_capital*constants.TAKE_PROFIT) or (final_balance <= self.broker_agent.start_capital*constants.STOP_LOSS)):
            logging.info(f'Stop trading at {final_balance}')
            self.stop_trade()
