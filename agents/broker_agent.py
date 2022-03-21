from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from alpaca_trade_api.common import URL
from config import alpaca, constants, hitbtc
from utils import datetime_utils
import ccxt
import pandas as pd
from datetime import datetime
import logging

class BrokerAgent():

    def __init__(self):
        self.url = URL('https://paper-api.alpaca.markets')
        self.api = REST(key_id=alpaca.CLIENT_ID,
                secret_key=alpaca.CLIENT_SECRET,
                base_url=self.url)
        self.account = None
        self.position = None
        logging.info('Established connection to Alpaca')
        logging.info(f'Created {self.__class__.__name__}')

    def get_balance(self, symbol=None):
        self.account = self.api.get_account()._raw
        self.position = self.api.get_position(symbol)._raw
        if(symbol is None):
            return self.account['cash']
        else:
            return(self.position['qty'])

    def ohlcv_data(self, symbol, timeframe=constants.TIMEFRAME):
        # since = datetime_utils.get_n_deltas_before_str(constants.LIMIT)
        # to = datetime_utils.get_today_str()
        ohlcv = self.api.get_crypto_bars(symbol, TimeFrame(timeframe, TimeFrameUnit.Minute), None, None, None, [alpaca.EXCHANGE]).df
        ohlcv.index = datetime_utils.convert_gmt_to_local(ohlcv.index)
        ohlcv = ohlcv.iloc[-(constants.LIMIT+1):]
        ohlcv.drop(['exchange', 'trade_count', 'vwap'], axis=1, inplace=True)
        ohlcv.columns=['Open', 'High', 'Low', 'Close', 'Volume']
        ohlcv.index.rename('Timestamp', inplace=True)
        return(ohlcv)

    #TODO: Why is not working?
    def latest_ohlcv(self, symbol):
        latest = self.api.get_latest_crypto_bar(symbol, alpaca.EXCHANGE)._raw
        print(latest)

    def ticker_price(self, symbol):
        quote = self.api.get_latest_crypto_quote(symbol, alpaca.EXCHANGE)._raw
        ticker = (float(quote['ap']) + float(quote['bp']))/2
        return(ticker)
        
    def market_buy_order(self, symbol, amount):
        res = self.api.submit_order(symbol, amount, 'buy')._raw
        return res

    def market_sell_order(self, symbol, amount):
        res = self.api.submit_order(symbol, amount, 'sell')._raw
        return res

    def limit_buy_order(self, symbol, amount, price):
        res = self.api.submit_order(symbol, amount, 'buy', 'limit', 'day', price)._raw
        return res

    def limit_sell_order(self, symbol, amount, price):
        res = self.api.submit_order(symbol, amount, 'sell', 'limit', 'day', price)._raw
        return res

    def orders(self, status='all'):
        res = self.api.list_orders(status)._raw
        return(res)
        
    def order_status(self, orderId):
        res = self.api.get_order_by_client_order_id(orderId)
        return res['status']

    def cancel_order(self, orderId):
        self.api.cancel_order(orderId)

    # def reset_balance(self):
    # TODO Manually
