import os
from io_utils import *
import pandas as pd

class CSVIO():

    def __init__(self):
        self.data_dir = 'data'
        self.agent_weights_file = 'agent_weights.csv'

    def save_weights(self, weights):
        weights_df = None
        weights_path = os.path.join(self.data_dir, self.agent_weights_file)
        if os.path.exists(weights_path):
            df = csv_to_df(weights_path)
            weights_df = pd.DataFrame(weights, index=[len(df)])
            weights_df = pd.concat([df, weights_df], axis=0, inplace=True)
        else:
            weights_df = pd.DataFrame(weights, index=[0])
        df_to_csv(weights_df, weights_path)

    def load_weights(self):
        weights_path = os.path.join(self.data_dir, self.agent_weights_file)
        if os.path.exists(weights_path):
            weights_df = csv_to_df(weights_path)
            return weights_df.iloc[-1].to_numpy()
        return None