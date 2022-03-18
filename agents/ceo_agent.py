import logging
from config import constants

class CEOAgent():

    def __init__(self, broker_agent, dao_agent):
        self.broker_agent = broker_agent
        self.dao_agent = dao_agent
        logging.info(f'Created {self.__class__.__name__}')

    def make_trade(self, trade):
        #TODO: Trade logic for CEO
        if(trade['action'] != 0):
            if(trade['action'] == 1):
                self.broker_agent.market_buy_order(constants.COIN, trade['quantity'])
            elif(trade['action'] == -1):
                self.broker_agent.market_sell_order(constants.COIN, trade['quantity'])
            #TODO: Update account book
            #self.dao_agent.add_data(trade)
        else:
            pass
