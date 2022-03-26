from .base_agent import BaseAgent
import time
import requests
import json
from datetime import datetime
from config import powerbi, constants

class PowerBIAgent(BaseAgent):
    
        def __init__(self, broker_agent, dao_agent):
            super().__init__()
            self.broker_agent = broker_agent
            self.dao_agent = dao_agent
            self.headers = {"Content-Type": "application/json"}
    
        def run(self):
            while True:
                self.update()
                time.sleep(constants.TICK)
    
        def update(self):
            #TODO Build objects to send to powerBI
            now = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
            hitprice, binance, diff, signal, profit = arbitrage_finder_two_markets()
            print(f'Time: {now}, Return: {profit:.4f} Hitbtc_Price : {hitprice:.2f}, Binance_Price :  {binance:.2f}, Difference : {abs(diff):.2f}, Arbitrage : {signal}')
            json_data = [{
                "Hitbtc_Price" :hitprice,
                "Binance_Price" :binance,
                "Difference" :abs(diff),
                "Arbitrage" :signal,
                "Return": profit,
                "Time" :now 
            }]

            #Send data to PowerBI Here
            response = requests.request(
                method="POST",
                url=powerbi.URL,
                headers=self.headers,
                data=json.dumps(json_data)
            )