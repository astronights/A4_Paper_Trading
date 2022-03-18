import os
from config import constants
from utils.io_utils import *
import logging
import pandas as pd

class DAOAgent():

    def __init__(self):
        self.account_book = None
        self.agent_weights = None
        logging.info(f'Created {self.__class__.__name__}')

    def add_data(self, data, type):
        if(type == Type.ACCOUNT_BOOK):
            if(self.account_book is None):
                self.account_book = pd.DataFrame(data, index=[0])
            else:
                df = pd.DataFrame(data, index=[len(self.account_book)])
                df = pd.concat([self.account_book, df], axis=0, copy=False)
                self.account_book = df
        else:
            if(self.agent_weights is None):
                self.agent_weights = pd.DataFrame(data, index=[0])
            else:
                df = pd.DataFrame(data, index=[len(self.agent_weights)])
                df = pd.concat([self.agent_weights, df], axis=0, copy=False)
                self.agent_weights = df

    def get_last_data(self, type):
        if(type == Type.ACCOUNT_BOOK):
            return self.account_book.iloc[-1] if self.account_book is not None else self.load_last_data(Type.ACCOUNT_BOOK)
        else:
            return self.agent_weights.iloc[-1] if self.agent_weights is not None else self.load_last_data(Type.AGENT_WEIGHTS)

    def get_all_data(self, type):
        if(type == Type.ACCOUNT_BOOK):
            return self.account_book if self.account_book is not None else self.load_last_data(Type.ACCOUNT_BOOK)
        else:
            return self.agent_weights if self.agent_weights is not None else self.load_last_data(Type.AGENT_WEIGHTS)


    def save_all_data(self):
        if(self.account_book is not None):
            account_book_path = os.path.join(constants.DATA_DIR, Type.ACCOUNT_BOOK.value)
            df_to_csv(self.account_book, account_book_path)
            logging.info(f'Saved {Type.ACCOUNT_BOOK}')
        if(self.agent_weights is not None):
            agent_weights_path = os.path.join(constants.DATA_DIR, Type.AGENT_WEIGHTS.value)
            df_to_csv(self.agent_weights, agent_weights_path)
            logging.info(f'Saved {Type.AGENT_WEIGHTS}')
        # df = None
        # path = os.path.join(constants.DATA_DIR, type.value)
        # if os.path.exists(path):
        #     old_df = csv_to_df(path)
        #     df = pd.DataFrame(data, index=[len(old_df)])
        #     df = pd.concat([old_df, df], axis=0, copy=False)
        # else:
        #     df = pd.DataFrame(data, index=[0])
        # print(df)
        # df_to_csv(df, path)

    def load_last_data(self, type):
        path = os.path.join(constants.DATA_DIR, type.value)
        if os.path.exists(path):
            df = csv_to_df(path)
            return df.iloc[-1]
        return None

    def load_all_data(self, type):
        path = os.path.join(constants.DATA_DIR, type.value)
        if os.path.exists(path):
            df = csv_to_df(path)
            return df
        return None
