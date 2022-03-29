from .base_agent import BaseAgent
import time
import requests
import json
from datetime import datetime
from config import powerbi, constants
import logging

class PowerBIAgent(BaseAgent):
    
        def __init__(self, decider_agent):
            super().__init__()
            self.decider_agent = decider_agent
            self.headers = {"Content-Type": "application/json"}
    
        def run(self):
            while True:
                if(self.decider_agent.updated):
                    self.update()
                    time.sleep(constants.TICK)
                else:
                    continue
    
        def update(self):
            #TODO Build objects to send to powerBI
            self.lock.acquire()
            now = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
            trade = self.decider_agent.trade
            self.decider_agent.updated = False
            json_data = [trade]

            #Send data to PowerBI Here
            response = requests.request(
                method="POST",
                url=powerbi.URL,
                headers=self.headers,
                data=json.dumps(json_data))
            
            logging.info('Updated data to PowerBI')
            self.lock.release()