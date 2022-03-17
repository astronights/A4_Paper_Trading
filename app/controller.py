from agents.signal_agents import *

class Controller():

    def __init__(self):
        self.agents = []

    def register_agents(self, agent):
        self.agents.append(agent)