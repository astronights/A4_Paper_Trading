from agents.signal_agents import ma_agent, bollinger_agent, rsi_agent, sentiment_agent
from agents import broker_agent, decider_agent, dao_agent, backtesting_agent, ceo_agent, macroecon_agent, var_agent, pnl_agent, powerbi_agent
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
        bollingerAgent = bollinger_agent.BollingerAgent(broker)
        rsiAgent = rsi_agent.RSIAgent(broker)
        sentimentAgent = sentiment_agent.SentimentAgent()
        self.signal_agents = [maAgent, bollingerAgent, rsiAgent, sentimentAgent]

        macroecon = macroecon_agent.MacroEconAgent()
        var = var_agent.VARAgent(broker)

        backtesting = backtesting_agent.BackTestingAgent(self.signal_agents, dao)

        pnl = pnl_agent.PNLAgent(broker, dao, backtesting)
        ceo = ceo_agent.CEOAgent(broker, dao)

        decider = decider_agent.DeciderAgent(self.signal_agents, broker, macroecon, var, dao, ceo)
        powerbi = powerbi_agent.PowerBIAgent(decider, broker)

        self.periodic_agents.extend([macroecon, var, pnl, decider, powerbi])
        logging.info('Registered agents')

    def start_agents(self):
        for agent in self.signal_agents+self.periodic_agents:
            agent.start()

    def stop_agents(self):
        for agent in self.signal_agents+self.periodic_agents:
            agent.stop()