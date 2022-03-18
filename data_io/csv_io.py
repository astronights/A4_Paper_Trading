from enum import Enum
import os
from .io_utils import *
import pandas as pd
from config import constants

class Type(Enum):
    AGENT_WEIGHTS = 'agent_weights.csv'
    ACCOUNT_BOOK = 'account_book.csv'

    
def save_data(data, type):
    df = None
    path = os.path.join(constants.DATA_DIR, type.value)
    if os.path.exists(path):
        old_df = csv_to_df(path)
        df = pd.DataFrame(data, index=[len(old_df)])
        df = pd.concat([old_df, df], axis=0, copy=False)
    else:
        df = pd.DataFrame(data, index=[0])
    print(df)
    df_to_csv(df, path)

def load_last_data(type):
    path = os.path.join(constants.DATA_DIR, type.value)
    if os.path.exists(path):
        df = csv_to_df(path)
        return df.iloc[-1]
    return None

def load_all_data(type):
    path = os.path.join(constants.DATA_DIR, type.value)
    if os.path.exists(path):
        df = csv_to_df(path)
        return df
    return None