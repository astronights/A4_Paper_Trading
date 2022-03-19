import logging
from config import constants
from utils.io_utils import Type

class CEOAgent():

    def __init__(self, broker_agent, dao_agent):
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent
        logging.info(f'Created {self.__class__.__name__}')

    def make_trade(self, trade):
        #TODO: Trade logic for CEO
        if(trade['type'] != 0):
            latest_candle = self.broker_agent.ohlcv_data(constants.SYMBOL, 1).to_dict()
            trade = self._update_trade_candle(trade, latest_candle)
            order = None
            if(trade['type'] == 1):
                order = self.broker_agent.market_buy_order(constants.COIN, trade['quantity'])
            elif(trade['type'] == -1):
                order = self.broker_agent.market_sell_order(constants.COIN, trade['quantity'])
            trade = self._populate_trade_order(trade, order)
            self.dao_agent.add_data(trade, Type.ACCOUNT_BOOK)
        else:
            pass

    def _update_trade_candle(self, trade, candle):
        for key in candle.keys():
            trade[key] = candle[key]
        return(trade)

    def _populate_trade_order(self, trade, order):
        trade['client_order_id'] = order['client_order_id']
        trade['status'] = order['status']
        trade['price'] = order['price']
        return(trade)
