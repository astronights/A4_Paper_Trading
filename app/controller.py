from agents.signal_agents import ma_agent, random_agent
from agents import broker_agent, decider_agent, account_agent, backtesting_agent
import logging

class Controller():

    def __init__(self):
        self.signal_agents = []
        self.periodic_agents = []

    def register_agents(self):
        logging.info('Registering Agents')
        broker = broker_agent.BrokerAgent()
        maAgent = ma_agent.MAAgent(broker)
        randomAgent = random_agent.RandomAgent()
        self.signal_agents.extend([maAgent, randomAgent])
        account = account_agent.AccountAgent()
        backtesting = backtesting_agent.BackTestingAgent(account, self.signal_agents)
        decider = decider_agent.DeciderAgent(self.signal_agents)
        self.periodic_agents.extend([backtesting, decider])
        logging.info('Registered agents')

    def start_agents(self):
        for agent in self.signal_agents+self.periodic_agents:
            agent.start()

    def stop_agents(self):
        for agent in self.signal_agents+self.periodic_agents:
            agent.stop()