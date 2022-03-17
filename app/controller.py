from agents.signal_agents import ma_agent
import logging

class Controller():

    def __init__(self):
        self.agents = []

    def register_agents(self):
        logging.info('Registering Agents...')
        maAgent = ma_agent.MAAgent()
        self.agents.append(maAgent)
        logging.info(f'{len(self.agents)} agents registered...')

    def start_agents(self):
        for agent in self.agents:
            print(f'Starting {agent.__str__()}...')
            agent.start()

    def stop_agents(self):
        for agent in self.agents:
            print(f'Stopping {agent.__str__()}...')
            agent.stop()