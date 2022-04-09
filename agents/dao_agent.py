import os
from config import constants
from utils import io_utils
from utils.io_utils import *
import logging
import numpy as np
import pandas as pd
from datetime import datetime

"""
DAO Agent to manage locally stored files and dataframes through the course of the run of the model
Tradebook, agent weights and CBR agent are managed.
"""
class DAOAgent():

    def __init__(self):
        # DataFrame consisting of order data
        # Rows order data
        # Column: Client_order_id, Action, Type, Price, Quantity, Status, Created_at, Updated_at, Symbol, Open, High, Low, Close, agent_weights, Balance, PNL
        # Index timestamp
        self.account_book = None

        # DataFrame consisting of the weights of the agents
        # Rows weights
        # Column agent name
        # Index timestamp
        self.agent_weights = self.load_all_data(Type.AGENT_WEIGHTS).tail(1)

        # Logistic Regression CBR Model
        self.cbr_model = io_utils.load_pickle(os.path.join(constants.DATA_DIR, 'cbr.pkl'))
        logging.info(f'Created {self.__class__.__name__}')

    """Get tradebook from market simulation run from simulation agent"""
    def get_historic_tradebook(self):
        return io_utils.csv_to_df(os.path.join(constants.DATA_DIR, 'tradebook.csv'))

    """Replace the entire dataframe with updated values"""
    def add_full_df(self, data, type):
        if(type == Type.ACCOUNT_BOOK):
            self.account_book = data
        else:
            self.agent_weights = data

    """
    Add one row of data to the dataframe
    Initialise new dataframe if doesn't exist, else append to existing dataframe
    """
    def add_data(self, data, type):
        now = datetime.now()
        if(type == Type.ACCOUNT_BOOK):
            if(self.account_book is None):
                self.account_book = pd.DataFrame(data, index=[now])
            else:
                df = pd.DataFrame(data, index=[len(self.account_book)])
                df = pd.concat([self.account_book, df], axis=0, copy=False)
                self.account_book = df
        else:
            if(self.agent_weights is None):
                self.agent_weights = pd.DataFrame(data, index=[now])
            else:
                df = pd.DataFrame(data, index=[len(self.agent_weights)])
                last_row_df = self.agent_weights.iloc[-1]

                # Append agent weights only if last row is not the same as the new row being added
                if(np.array_equal(last_row_df.values,df.values)):
                    pass
                else:
                    df = pd.concat([self.agent_weights, df], axis=0, copy=False)
                    self.agent_weights = df

    """
    Get the last row from the dataframe
    If dataframe exists in memory, get last row
    Else get last row from file
    """
    def get_last_data(self, type):
        if(type == Type.ACCOUNT_BOOK):
            return self.account_book.iloc[-1] if self.account_book is not None else self.load_last_data(Type.ACCOUNT_BOOK)
        else:
            return self.agent_weights.iloc[-1] if self.agent_weights is not None else self.load_last_data(Type.AGENT_WEIGHTS)

    """
    Get complete dataframe
    If dataframe exists in memory, get entire dataframe
    Else get entire dataframe from file
    """
    def get_all_data(self, type):
        if(type == Type.ACCOUNT_BOOK):
            return self.account_book if self.account_book is not None else self.load_all_data(Type.ACCOUNT_BOOK)
        else:
            return self.agent_weights if self.agent_weights is not None else self.load_all_data(Type.AGENT_WEIGHTS)

    """Save all managed data to CSV files"""
    def save_all_data(self):

        # Save Account book to file if it exists
        # Only save completed trades
        if(self.account_book is not None):
            account_book_path = os.path.join(constants.DATA_DIR, Type.ACCOUNT_BOOK.value)
            updated_df = None
            if(os.path.exists(account_book_path)):
                old_df = csv_to_df(account_book_path)
                updated_df = pd.concat([old_df, self.account_book[self.account_book['PNL'].notnull()]], axis=0, copy=False)
            else:
                updated_df = self.account_book
            df_to_csv(updated_df, account_book_path)
            logging.info(f'Saved {Type.ACCOUNT_BOOK}')
            
            # Retain trades that aren't completed (buys without sells)
            self.account_book = self.account_book[self.account_book['PNL'].isnull()]

        # Update agent weights if they exist
        if(self.agent_weights is not None):
            agent_weights_path = os.path.join(constants.DATA_DIR, Type.AGENT_WEIGHTS.value)
            old_df = csv_to_df(agent_weights_path)
            updated_df = pd.concat([old_df, self.agent_weights], axis=0, copy=False)
            df_to_csv(updated_df, agent_weights_path)
            logging.info(f'Saved {Type.AGENT_WEIGHTS}')

        # Save CBR model to file
        save_pickle(self.cbr_model, os.path.join(constants.DATA_DIR, 'cbr.pkl'))
        logging.info(f'Saved CBR Model')

    """Load last row of data from CSV file"""
    def load_last_data(self, type):
        path = os.path.join(constants.DATA_DIR, type.value)
        if os.path.exists(path):
            df = csv_to_df(path)
            return df.iloc[-1]
        return None

    """Load all data from CSV file"""
    def load_all_data(self, type):
        path = os.path.join(constants.DATA_DIR, type.value)
        if os.path.exists(path):
            df = csv_to_df(path)
            return df
        return None