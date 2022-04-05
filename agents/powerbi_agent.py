from .base_agent import BaseAgent
import time
import requests
import json
from datetime import datetime
from config import powerbi, constants
import logging

class PowerBIAgent(BaseAgent):
    
        def __init__(self, decider_agent, broker_agent):
            super().__init__()
            self.decider_agent = decider_agent
            self.broker_agent = broker_agent
            self.headers = {"Content-Type": "application/json"}
    
        def run(self):
            while True:
                if(self.decider_agent.updated):
                    self.update()
                    time.sleep(constants.TICK)
                else:
                    continue
    
        def update(self):
            self.lock.acquire()
            
            # Build objects to send to powerBI
            trade = self.decider_agent.trade
            trade['Start_Capital'] = self.broker_agent.start_capital
            trade['Stop_Loss'] = trade['Start_Capital']*constants.STOP_LOSS
            trade['Take_Profit'] = trade['Start_Capital']*constants.TAKE_PROFIT
            self.decider_agent.updated = False
            json_data = [trade]

            # Send data to PowerBI Here
            response = requests.request(
                method="POST",
                url=powerbi.URL,
                headers=self.headers,
                data=json.dumps(json_data))
            logging.info(f'PowerBI Response: {response.text}')
            logging.info('Updated data to PowerBI')
            self.lock.release() 