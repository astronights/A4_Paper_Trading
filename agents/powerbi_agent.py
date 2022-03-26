from .base_agent import BaseAgent
import time
import requests
import json
from datetime import datetime
from config import powerbi, constants

class PowerBIAgent(BaseAgent):
    
        def __init__(self, dao_agent):
            super().__init__()
            self.dao_agent = dao_agent
            self.headers = {"Content-Type": "application/json"}
    
        def run(self):
            while True:
                self.update()
                time.sleep(constants.TICK)
    
        def update(self):
            #TODO Build objects to send to powerBI
            now = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
            trade = self.dao_agent.trade_latest
            json_data = [trade]

            #Send data to PowerBI Here
            response = requests.request(
                method="POST",
                url=powerbi.URL,
                headers=self.headers,
                data=json.dumps(json_data)
            )