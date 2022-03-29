# import time
# import logging
# import numpy as np
# from .base_signal_agent import BaseSignalAgent
# from threading import Thread
# from config import constants
# from config.constants import *

# # DRL models from ElegantRL: https://github.com/AI4Finance-Foundation/ElegantRL
# import torch
# from elegantrl.agents.agent import AgentDDPG
# from elegantrl.agents.agent import AgentPPO
# from elegantrl.agents.agent import AgentSAC
# from elegantrl.agents.agent import AgentTD3
# from elegantrl.train.config import Arguments
# # from elegantrl.agents.agent import AgentA2C
# from elegantrl.train.run import train_and_evaluate, init_agent

# MODELS = {"ddpg": AgentDDPG, "td3": AgentTD3, "sac": AgentSAC, "ppo": AgentPPO}
# OFF_POLICY_MODELS = ["ddpg", "td3", "sac"]
# ON_POLICY_MODELS = ["ppo"]

# class DRLAgent(BaseSignalAgent):
    
#     def __init__(self, broker_agent):
#         super().__init__()
#         self.broker_agent = broker_agent

#     def run(self):
#         while True:
#             self.signal()
#             time.sleep(constants.TICK)

#     def signal(self):
#         self.lock.acquire()
#         df = self.broker_agent.ohlcv_data(SYMBOL,TIMEFRAME)
#         df['SMA_20'] = df[constants.PRICE_COL].rolling(20).mean()
#         df['STD_20'] = df[constants.PRICE_COL].rolling(20).std()
#         df['LOW_Band_20'] = df['SMA_20'] - df['STD_20'] * 2
#         df['HIGH_Band_20'] = df['SMA_20'] + df['STD_20'] * 2
        
#         df['Sell_Signal'] = np.where(df[constants.PRICE_COL] >= df['HIGH_Band_20'], 1, 0)
#         df['Sell_Position'] = df['Sell_Signal'].diff()
#         df['Buy_Signal'] = np.where(df[constants.PRICE_COL] <= df['LOW_Band_20'], 1, 0)
#         df['Buy_Position'] = df['Buy_Signal'].diff()
        
#         if df.iloc[-1]['Buy_Position']==-1:
#             self.signals.append(1)
#         elif df.iloc[-1]['Sell_Position']==-1:
#             self.signals.append(-1)
#         else:
#             self.signals.append(0)
#         self.lock.release()
#         logging.info(f'FinRL Signal: {self.signals[-1]}')

#     def get_model(self, model_name, model_kwargs):
#         env_config = {
#             # "price_array": self.price_array,
#             # "tech_array": self.tech_array,
#             # "turbulence_array": self.turbulence_array,
#             # "if_train": True,
#         }
#         env = self.env(config=env_config)
#         env.env_num = 1

#         agent = MODELS[model_name]
#         if model_name not in MODELS:
#             raise NotImplementedError("NotImplementedError")
#         model = Arguments(agent=agent, env=env)
#         model.if_off_policy = model_name in OFF_POLICY_MODELS
#         if model_kwargs is not None:
#             try:
#                 model.learning_rate = model_kwargs["learning_rate"]
#                 model.batch_size = model_kwargs["batch_size"]
#                 model.gamma = model_kwargs["gamma"]
#                 model.seed = model_kwargs["seed"]
#                 model.net_dim = model_kwargs["net_dimension"]
#                 model.target_step = model_kwargs["target_step"]
#                 model.eval_gap = model_kwargs["eval_gap"]
#                 model.eval_times = model_kwargs["eval_times"]
#             except BaseException:
#                 raise ValueError(
#                     "Fail to read arguments, please check 'model_kwargs' input."
#                 )
#         return model

#     def train_model(self, model, cwd, total_timesteps=5000):
#         model.cwd = cwd
#         model.break_step = total_timesteps
#         train_and_evaluate(model)
