#Testing Broker
from agents import broker_agent

broker = broker_agent.BrokerAgent()

#Check Ticker
# print(broker.latest_ohlcv('BTCUSD'))
print(broker.orders()[0]._raw)