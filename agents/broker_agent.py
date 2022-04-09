from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit, APIError
from alpaca_trade_api.common import URL
from config import alpaca, constants
from utils import datetime_utils
import logging

"""Broker Agent to interact with the Alpaca Trade and Market APIs for Paper Trading"""
class BrokerAgent():

    def __init__(self):
        self.url = URL('https://paper-api.alpaca.markets')

        # Alpaca API credentials taken from alpaca config
        self.api = REST(key_id=alpaca.CLIENT_ID,
                secret_key=alpaca.CLIENT_SECRET,
                base_url=self.url)
        self.ohlcv_mappings = {'t': 'Timestamp', 'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}
        logging.info('Established connection to Alpaca')
        logging.info(f'Created {self.__class__.__name__}')

        # Set initial variables
        self.start_capital = self.get_balance('cash')
        constants.START_CAPITAL = self.start_capital
        self.error_flag = False
        self.account = None
        self.position = None

    """
    Get current balance from Alpaca account
    Passing symbol 'cash' returns cash balance
    Passing symbol of the asset returns position balance
    """
    def get_balance(self, symbol):
        self.account = self.api.get_account()._raw

        # Alpaca throws error if position is empty for asset
        try:
            self.position = self.api.get_position('BTCUSD')._raw
        except APIError:
            self.position = {'qty': 0}
        if(symbol == 'cash'):
            return(float(self.account['cash']))
        else:
            return(float(self.position['qty']))

    """
    Get historical OHLCV data for asset
    Timeframe is passed to specify the frequency at which bars are returned
    """
    def ohlcv_data(self, symbol, timeframe=constants.TIMEFRAME):
        ohlcv = self.api.get_crypto_bars(symbol, TimeFrame(timeframe, TimeFrameUnit.Minute), None, None, None, [alpaca.EXCHANGE]).df
        
        # Timezone converted from GMT to local time
        ohlcv.index = datetime_utils.convert_gmt_to_local(ohlcv.index)

        # Alpaca glitches sometimes return lesser than desired bars. 
        # This could lead to errors in agent functionality, so we log out a warning.
        if(len(ohlcv) < constants.LIMIT and self.error_flag == False):
            logging.warning(f'{len(ohlcv)}/{constants.LIMIT} bars for {symbol} available. Might create errors...')
            self.error_flag = True
        
        # If we have more than the desired number of bars, we drop the excess
        ohlcv = ohlcv.iloc[-(constants.LIMIT+1):]
        ohlcv.drop(['exchange', 'trade_count', 'vwap'], axis=1, inplace=True)
        ohlcv.columns=['Open', 'High', 'Low', 'Close', 'Volume']
        ohlcv.index.rename('Timestamp', inplace=True)
        return(ohlcv)

    """Get the latest OHLCV bar from Alpaca"""
    def latest_ohlcv(self, symbol):
        latest = self.api.get_latest_crypto_bar(symbol, alpaca.EXCHANGE)._raw
        latest_ret = {}

        # Filter the relevant fields
        for key in self.ohlcv_mappings.keys():
            latest_ret[self.ohlcv_mappings[key]] = latest.pop(key)
        return(latest_ret)

    """Get the latest traded price of the asset by averaging the best ask and best bid"""
    def ticker_price(self, symbol):
        quote = self.api.get_latest_crypto_quote(symbol, alpaca.EXCHANGE)._raw
        ticker = (float(quote['ap']) + float(quote['bp']))/2
        return(ticker)
        
    """Place a market buy order for the specified asset and amount"""
    def market_buy_order(self, symbol, amount):
        res = self.api.submit_order(symbol, amount, 'buy')._raw
        return res

    """Place a market sell order for the specified asset and amount"""
    def market_sell_order(self, symbol, amount):
        res = self.api.submit_order(symbol, amount, 'sell')._raw
        return res

    """Place a limit buy order for the specified asset, amount and price"""
    def limit_buy_order(self, symbol, amount, price):
        res = self.api.submit_order(symbol, amount, 'buy', 'limit', 'day', price)._raw
        return res

    """Place a limit sell order for the specified asset, amount and price"""
    def limit_sell_order(self, symbol, amount, price):
        # Place limit sell order
        res = self.api.submit_order(symbol, amount, 'sell', 'limit', 'day', price)._raw
        return res

    """Get all orders from the account at Alpaca depending of status (Default all)"""
    def orders(self, status='all'):
        res = self.api.list_orders(status)
        return([] if res is None else res)

    """Get details of a single order from Alpaca by clientOrderID"""
    def order_single(self, orderId):
        # Get details for one order
        res = self.api.get_order_by_client_order_id(orderId)
        return res._raw

    """Cancel an onder posted to the Alpaca paper trading account"""
    def cancel_order(self, orderId):
        # Cancel single order
        self.api.cancel_order(orderId)
