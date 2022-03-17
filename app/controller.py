from agents.signal_agents import ma_agent
from agents import broker_agent, decider_agent
import logging

class Controller():

    def __init__(self):
        self.agents = []

    def register_agents(self):
        logging.info('Registering Agents...')
        broker = broker_agent.BrokerAgent()
        maAgent = ma_agent.MAAgent(broker)
        self.agents.append(maAgent)
        decider = decider_agent.DeciderAgent(self.agents)
        logging.info(f'{len(self.agents)} agents registered...')

    def start_agents(self):
        for agent in self.agents:
            print(f'Starting {agent.__str__()}...')
            agent.start()

    def stop_agents(self):
        for agent in self.agents:
            print(f'Stopping {agent.__str__()}...')
            agent.stop()