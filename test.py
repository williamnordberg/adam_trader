import pandas as pd
import logging
from sklearn.tree import DecisionTreeRegressor
from sklearn.impute import SimpleImputer
from typing import Tuple
from time import sleep

from database import save_value_to_database, read_database
from update_dataset_yahoo import update_yahoo_data
from update_dataset_macro import update_macro_economic
from update_dataset_internal_factors import update_internal_factors, UpdateInternalFactorsError
from handy_modules import compare_predicted_price, get_bitcoin_price, should_update, save_update_time




def update_dataset():
    update_internal_factors()




while True:
    update_dataset()
    print('continue')
    sleep(10)
