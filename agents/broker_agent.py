from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit, APIError
from alpaca_trade_api.common import URL
from config import alpaca, constants, hitbtc
from utils import datetime_utils
# import ccxt
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
        self.ohlcv_mappings = {'t': 'Timestamp', 'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}
        logging.info('Established connection to Alpaca')
        logging.info(f'Created {self.__class__.__name__}')
        self.start_capital = self.get_balance('cash')
        constants.START_CAPITAL = self.start_capital

    def get_balance(self, symbol):
        # Get Cash/BTC balance from Alpaca
        self.account = self.api.get_account()._raw
        try:
            self.position = self.api.get_position('BTCUSD')._raw
        except APIError:
            self.position = {'qty': 0}
        if(symbol == 'cash'):
            return(float(self.account['cash']))
        else:
            return(float(self.position['qty']))

    def ohlcv_data(self, symbol, timeframe=constants.TIMEFRAME):
        # Get OHLCV data on periods of time from Alpaca
        ohlcv = self.api.get_crypto_bars(symbol, TimeFrame(timeframe, TimeFrameUnit.Minute), None, None, None, [alpaca.EXCHANGE]).df
        ohlcv.index = datetime_utils.convert_gmt_to_local(ohlcv.index)
        if(len(ohlcv) < constants.LIMIT):
            logging.warning(f'{len(ohlcv)}/{constants.LIMIT} bars for {symbol} available. Please rerun later...')
        ohlcv = ohlcv.iloc[-(constants.LIMIT+1):]
        ohlcv.drop(['exchange', 'trade_count', 'vwap'], axis=1, inplace=True)
        ohlcv.columns=['Open', 'High', 'Low', 'Close', 'Volume']
        ohlcv.index.rename('Timestamp', inplace=True)
        return(ohlcv)

    def latest_ohlcv(self, symbol):
        # Get latest OHLCV bar for the crypto from Alpaca
        latest = self.api.get_latest_crypto_bar(symbol, alpaca.EXCHANGE)._raw
        latest_ret = {}
        for key in self.ohlcv_mappings.keys():
            latest_ret[self.ohlcv_mappings[key]] = latest.pop(key)
        return(latest_ret)

    def ticker_price(self, symbol):
        # Get current ticker price and average to get trading price
        quote = self.api.get_latest_crypto_quote(symbol, alpaca.EXCHANGE)._raw
        ticker = (float(quote['ap']) + float(quote['bp']))/2
        return(ticker)
        
    def market_buy_order(self, symbol, amount):
        # Place market buy order
        res = self.api.submit_order(symbol, amount, 'buy')._raw
        return res

    def market_sell_order(self, symbol, amount):
        # Place market sell order
        res = self.api.submit_order(symbol, amount, 'sell')._raw
        return res

    def limit_buy_order(self, symbol, amount, price):
        # Place limit buy order
        res = self.api.submit_order(symbol, amount, 'buy', 'limit', 'day', price)._raw
        return res

    def limit_sell_order(self, symbol, amount, price):
        # Place limit sell order
        res = self.api.submit_order(symbol, amount, 'sell', 'limit', 'day', price)._raw
        return res

    def orders(self, status='all'):
        # Get all orders
        res = self.api.list_orders(status)
        return([] if res is None else res)

    def order_single(self, orderId):
        # Get details for one order
        res = self.api.get_order_by_client_order_id(orderId)
        return res._raw

    def cancel_order(self, orderId):
        # Cancel single order
        self.api.cancel_order(orderId)
