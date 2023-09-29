import math as math
import warnings
import pandas as pd
import numpy as np
from settings.features import broad,narrow, wise, gaia, morph
from utils.correct_extinction import correction


def preprocess(data, correct_ext  = True, value_to_insert=99):
    data = wiseflux2vega(data, value_to_insert=99)
    data[gaia] = data[gaia].replace(np.nan, 99)
    data = data.dropna(subset=broad+narrow+morph, how='any')
    data = insert_missing(data, broad+narrow, error=0.5, value_to_insert=value_to_insert)
    data = insert_missing(data, wise, error=0.5, value_to_insert=value_to_insert)
    if correct_ext:
        data = correction(data, splus_bands=True, wise_bands = True)
    return data


def wiseflux2vega(data, value_to_insert =99):
    data.loc[data["FW1"]==0, "FW1"] = 0.001
    data.loc[data["FW2"]==0, "FW2"] = 0.001

    data["W1_MAG"] = -2.5 * np.log10(data["FW1"]) + 22.5
    data["W2_MAG"] = -2.5 * np.log10(data["FW2"]) + 22.5
    data["e_W1_MAG"] = 2.5 * data["e_FW1"] / (data["FW1"] * np.log(10))
    data["e_W2_MAG"] = 2.5  * data["e_FW1"] / (data["FW2"] * np.log(10)) 

    # insert missing value
    data['W1_MAG'].fillna(value_to_insert, inplace=True)
    data['W2_MAG'].fillna(value_to_insert, inplace=True)
    data.loc[data["W1_MAG"]>25, "W1_MAG"] = value_to_insert
    data.loc[data["W2_MAG"]>25, "W2_MAG"] = value_to_insert
    return data


def insert_missing(data, list_filter, error=0.5, value_to_insert=99):
    for filter in list_filter:
        data.loc[data["e_"+filter]>error, filter] = value_to_insert    
    return data

