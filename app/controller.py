from agents.signal_agents import ma_agent, random_agent
from agents import broker_agent, decider_agent, dao_agent, backtesting_agent, ceo_agent, macroecon_agent, pnl_agent, powerbi_agent
import logging

class Controller():

    def __init__(self):
        self.signal_agents = []
        self.periodic_agents = []

    def register_agents(self):
        logging.info('Registering Agents')
        dao = dao_agent.DAOAgent()
        broker = broker_agent.BrokerAgent()

        maAgent = ma_agent.MAAgent(broker)
        randomAgent = random_agent.RandomAgent()
        self.signal_agents.extend([maAgent, randomAgent])

        macroecon = macroecon_agent.MacroEconAgent()

        pnl = pnl_agent.PNLAgent(broker, dao)
        ceo = ceo_agent.CEOAgent(broker, dao)
        powerbi = powerbi_agent.PowerBIAgent(broker, dao)

        backtesting = backtesting_agent.BackTestingAgent(self.signal_agents, dao)
        decider = decider_agent.DeciderAgent(self.signal_agents, dao, ceo)

        self.periodic_agents.extend([macroecon, pnl, backtesting, decider, powerbi])
        logging.info('Registered agents')

    def start_agents(self):
        for agent in self.signal_agents+self.periodic_agents:
            agent.start()

    def stop_agents(self):
        for agent in self.signal_agents+self.periodic_agents:
            agent.stop()