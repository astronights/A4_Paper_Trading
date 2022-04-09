import logging
from config import constants
from utils.io_utils import Type

"""
CEOAgent to evaluate trades and execute by sending to Broker Agent
Executed trades are also refetched and updated to populate the Account Book
"""
class CEOAgent():

    def __init__(self, broker_agent, dao_agent):
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent
        logging.info(f'Created {self.__class__.__name__}')

    """
    Evaluate trade received from Decider Agent against current portfolio and risk management
    Make trade if conditions are satisfied
    """
    def make_trade(self, trade):

        # Collect latest candlestick data and update trade object
        latest_candle = self.broker_agent.latest_ohlcv(constants.SYMBOL)
        trade = self._update_trade_candle(trade, latest_candle)

        # Verify stop loss and take profit if no trade action is specified
        if(trade['Action'] == 'none'):
            self._check_stop_loss_take_profit(trade, latest_candle)

        # Update trade price if absent
        trade_price = trade['Price'] if trade['Price'] is not None else latest_candle[constants.PRICE_COL]
        order = None

        # Verify if equity value exists and if so, place order
        if(trade['Action'] == 'buy'):
            if(trade['Quantity']*trade_price < self.broker_agent.get_balance('cash')):
                if(trade['Type'] == 'market'):
                    order = self.broker_agent.market_buy_order(constants.SYMBOL, trade['Quantity'])
                else:
                    order = self.broker_agent.limit_buy_order(constants.SYMBOL, trade['Quantity'], trade_price)

                # Update trade with completed order details
                trade = self._update_book(trade, order)
            else:
                logging.info(f'Insufficient balance to buy {trade["Quantity"]} {constants.COIN} @ {trade_price}, available balance: {self.broker_agent.get_balance("cash")}')
        elif(trade['Action'] == 'sell'):
            if(trade['Quantity'] <= self.broker_agent.get_balance(constants.SYMBOL) and trade['Quantity'] > 0):
                if(trade['Type'] == 'market'):
                    order = self.broker_agent.market_sell_order(constants.SYMBOL, trade['Quantity'])
                else:
                    order = self.broker_agent.limit_sell_order(constants.SYMBOL, trade['Quantity'], trade_price)
                    
                # Update trade with completed order details
                trade = self._update_book(trade, order)
            else:
                logging.info(f'Insufficient balance to sell {trade["Quantity"]} {constants.COIN} @ {trade_price}, available balance: {self.broker_agent.get_balance(constants.SYMBOL)}')
        else:
            logging.info(f'No trade action specified @ {latest_candle["Timestamp"]}')
        
        # Update trade balance
        trade['Balance'] = self.broker_agent.get_balance('cash')
        return(trade)

    """Update trade object with OHLCV from latest candlestick"""
    def _update_trade_candle(self, trade, candle):
        for key in candle.keys():
            trade[key] = candle[key]
        del trade['Timestamp']
        return(trade)

    """Update trade object with fields from completed trade"""
    def _populate_trade_order(self, trade, order):
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

    """Update trade and send data to trade book"""
    def _update_book(self, trade, order):
        trade = self._populate_trade_order(trade, order)
        self.dao_agent.add_data(trade, Type.ACCOUNT_BOOK)
        return(trade)

    """
    Check if current position had potential to cross stop loss or take profit
    Modify trade to attain criteria and send for execution
    """
    def _check_stop_loss_take_profit(self, trade, latest_candle):

        # Get cash + asset balance
        balance = self.broker_agent.get_balance('cash') + (self.broker_agent.get_balance(constants.SYMBOL)*latest_candle[constants.PRICE_COL])
        trade['Type'] = 'market'

        # Take Profit Criteria
        if(balance > (self.broker_agent.start_capital*constants.TAKE_PROFIT)):
            logging.info(f'Take profit and stop trading')
            trade['Action'] = 'sell'
            trade['Quantity'] = self.broker_agent.get_balance(constants.SYMBOL)
            trade['Price'] = latest_candle[constants.PRICE_COL]
        
        # Stop Loss Criteria
        elif(balance < (self.broker_agent.start_capital*constants.STOP_LOSS)):
            logging.info(f'Stop loss and stop trading')
            trade['Action'] = 'sell'
            trade['Quantity'] = self.broker_agent.get_balance(constants.SYMBOL)
            trade['Type'] = 'market'
            trade['Price'] = latest_candle[constants.PRICE_COL]
