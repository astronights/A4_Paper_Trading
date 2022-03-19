import ccxt
import pandas as pd
from datetime import datetime
from config import constants, hitbtc
import logging

class BrokerAgent():

    def __init__(self):
        self.hitbtc = ccxt.hitbtc({'apiKey': hitbtc.apiKey, 'secret': hitbtc.secret,
                          'urls': {'api': {'private': 'https://api.demo.hitbtc.com'}}})
        logging.info('Established connection to HitBTC')
        logging.info(f'Created {self.__class__.__name__}')

    def get_balance(self, symbol):
        balance = self.hitbtc.fetch_balance({'type': 'trading'})
        if(symbol in balance['info'].keys()):
            return balance['info'][symbol]['available']
        return None

    def ohlcv_data(self, symbol, timeframe=constants.TIMEFRAME, limit=constants.LIMIT):
        ohlcv = self.hitbtc.fetch_ohlcv(symbol, timeframe, limit, params={'sort': 'DESC'})
        df = pd.DataFrame(ohlcv, columns=['TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df.index = df.TimeStamp.apply(lambda x: datetime.fromtimestamp(x / 1000.0))
        df.drop(['TimeStamp'], axis=1, inplace=True)
        return df

    def ticker_price(self, symbol):
        ticker_price = self.hitbtc.fetch_ticker(symbol)['info']
        return (float(ticker_price['bid']) + float(ticker_price['ask'])/2)

    def market_buy_order(self, symbol, amount):
        res = self.hitbtc.create_market_buy_order(symbol, amount)
        return res['price']

    def market_sell_order(self, symbol, amount):
        res = self.hitbtc.create_market_sell_order(symbol, amount)
        return res['price']

    def limit_buy_order(self, symbol, amount, price):
        res = self.hitbtc.create_limit_buy_order(symbol, amount, price)
        return res['clientOrderId']

    def limit_sell_order(self, symbol, amount, price):
        res = self.hitbtc.create_limit_sell_order(symbol, amount, price)
        return res['clientOrderId']

    def order_status(self, orderId, symbol):
        res = self.hitbtc.fetch_order(orderId, symbol)
        return res['status']

    def cancel_order(self, orderId, symbol):
        self.hitbtc.cancel_order(orderId, symbol)