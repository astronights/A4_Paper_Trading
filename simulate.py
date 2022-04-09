from agents import simulate_agent
import logging

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""Run simulation for historic trade period"""
if __name__=='__main__':
    logging.info(f'Starting app')
    sim = simulate_agent.SimulateAgent()
    sim.simulate()