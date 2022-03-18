from config import constants
from data_io import csv_io
import logging

class AccountAgent():

    def __init__(self):
        self.account_book = None
        logging.info(f'Created {self.__class__.__name__}')

    def save_data(self, data):
        csv_io.save_data(data, csv_io.Type.ACCOUNT_BOOK)
    
    def load_from_file(self):
        return(csv_io.load_all_data(csv_io.Type.ACCOUNT_BOOK))
