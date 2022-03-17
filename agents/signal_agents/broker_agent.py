import ccxt

class BrokerAgent():

     def __init__():
        hitbtc = ccxt.hitbtc({'apiKey': api_key,
                          'secret': secret,
                          'urls': {
                              'api': {
                                  'private': 'https://api.demo.hitbtc.com'
                              }
                          },
                          'verbose': False})