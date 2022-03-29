#Testing Broker
from agents import broker_agent

broker = broker_agent.BrokerAgent()

#Check Ticker
broker.ohlcv_data('BTCUSD')