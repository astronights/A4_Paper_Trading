import logging
from config import constants
from utils.io_utils import Type

class CEOAgent():

    def __init__(self, broker_agent, dao_agent):
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent
        logging.info(f'Created {self.__class__.__name__}')

    def make_trade(self, trade):
        latest_candle = self.broker_agent.latest_ohlcv(constants.SYMBOL)
        trade = self._update_trade_candle(trade, latest_candle)
        if(trade['Action'] == 0):
            self._check_stop_loss_take_profit(trade, latest_candle)
        order = None
        trade_price = trade['Price'] if trade['Price'] is not None else latest_candle[constants.PRICE_COL]
        print(trade)
        if(trade['Action'] == 'buy'):
            if(trade['Quantity']*trade_price < self.broker_agent.get_balance('cash')):
                if(trade['Type'] == 'market'):
                    order = self.broker_agent.market_buy_order(constants.SYMBOL, trade['Quantity'])
                else:
                    order = self.broker_agent.limit_buy_order(constants.SYMBOL, trade['Quantity'], trade_price)
                trade = self._update_book(trade, order)
            else:
                logging.info(f'Insufficient balance to buy {trade["Quantity"]} {constants.COIN} @ {trade_price}, available balance: {self.broker_agent.get_balance("cash")}')
        elif(trade['Action'] == 'sell'):
            if(trade['Quantity'] <= self.broker_agent.get_balance(constants.SYMBOL)):
                if(trade['Type'] == 'market'):
                    order = self.broker_agent.market_sell_order(constants.SYMBOL, trade['Quantity'])
                else:
                    order = self.broker_agent.limit_sell_order(constants.SYMBOL, trade['Quantity'], trade_price)
                trade = self._update_book(trade, order)
            else:
                logging.info(f'Insufficient balance to sell {trade["Quantity"]} {constants.COIN} @ {trade_price}, available balance: {self.broker_agent.get_balance(constants.SYMBOL)}')
        else:
            logging.info(f'No trade action specified @ {latest_candle["Timestamp"]}')
        self.dao_agent.trade_latest = trade
        

    def _update_trade_candle(self, trade, candle):
        for key in candle.keys():
            trade[key] = candle[key]
        return(trade)

    def _populate_trade_order(self, trade, order):
        #TODO Add PnL value
        u_order = self.broker_agent.order_single(order['client_order_id'])
        trade['Client_order_id'] = u_order['client_order_id']
        trade['Action'] = u_order['side']
        trade['Type'] = u_order['type']
        trade['Price'] = float(u_order['filled_avg_price'])
        trade['Quantity'] = float(u_order['qty'])
        trade['Status'] = u_order['status']
        trade['Created_at'] = u_order['created_at']
        trade['Updated_at'] = u_order['updated_at']
        trade['Symbol'] = u_order['symbol']
        trade['Balance'] = self.broker_agent.get_balance('cash')
        return(trade)

    def _update_book(self, trade, order):
        print(order)
        trade = self._populate_trade_order(trade, order)
        self.dao_agent.add_data(trade, Type.ACCOUNT_BOOK)
        return(trade)

    def _check_stop_loss_take_profit(self, trade, latest_candle):
        balance = self.broker_agent.get_balance('cash') + self.broker_agent.get_balance(constants.SYMBOL)*latest_candle[constants.PRICE_COL]
        if(balance > (constants.START_CAPITAL*constants.TAKE_PROFIT)):
            logging.info(f'Take profit and stop trading')
            trade['Action'] = 'sell'
            trade['Quantity'] = self.broker_agent.get_balance(constants.SYMBOL)
            trade['Type'] = 'limit'
            trade['Price'] = latest_candle[constants.PRICE_COL]
        elif(balance < (constants.START_CAPITAL*constants.STOP_LOSS)):
            logging.info(f'Stop loss and stop trading')
            trade['Action'] = 'sell'
            trade['Quantity'] = self.broker_agent.get_balance(constants.SYMBOL)
            trade['Type'] = 'limit'
            trade['Price'] = latest_candle[constants.PRICE_COL]
