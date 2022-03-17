import ccxt
import pandas as pd
from datetime import datetime
from config.constants import *
from config.hitbtc import *
import logging

class BrokerAgent():

    def __init__(self):
        logging.info(f'BrokerAgent created...')
        self.ohlcv_limit = 100
        self.price_col = 'Close'
        self.hitbtc = ccxt.hitbtc({'apiKey': apiKey, 'secret': secret,
                          'urls': {'api': {'private': 'https://api.demo.hitbtc.com'}}})

    def get_balance(self, symbol):
        balance = self.hitbtc.fetch_balance({'type': 'trading'})
        if(symbol in balance['info'].keys()):
            return balance['info'][symbol]['available']
        return None

    def ohlcv_data(self, symbol):
        ohlcv = self.hitbtc.fetch_ohlcv(symbol, TIMEFRAME, self.ohlcv_limit, params={'sort': 'DESC'})
        df = pd.DataFrame(ohlcv, columns=['TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df.index = df.TimeStamp.apply(lambda x: datetime.fromtimestamp(x / 1000.0))
        df.drop(['TimeStamp'], axis=1, inplace=True)
        return df

    def ticker_price(self, symbol):
        ticker_price = self.hitbtc.fetch_ticker(symbol)['info']
        print(ticker_price)
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