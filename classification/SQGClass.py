import pickle
import pandas as pd
import numpy as np
from astropy import units as u
# from astroquery.utils.tap.core import TapPlus
from astropy.coordinates import SkyCoord
import requests
from settings.features import morph, broad, narrow, wise, gaia
from utils.preprocessing import preprocess
import os 


class SQGClass:
    __author__ = "Lilianne Nakazono"
    __version__ = "0.3.0"
    _pos = ["RA", "DEC"]
    
    # _morph, _feat, _wise = morph, splus, wise

    def __init__(self,  verbose=False):
        self.verbose = verbose
        self.feat_gaia = broad+narrow+wise+morph+gaia
        self.feat = broad+narrow+wise+morph

        try:
            if self.verbose:
                print("Loading model...")
            with open("models/rf_broad_narrow_wise_morph_gaia.sav", "rb") as f:
                self.model_gaia = pickle.load(f)
            with open("models/rf_broad_narrow_wise_morph.sav", "rb") as f:
                self.model = pickle.load(f) 
        except:
            raise ValueError("Loading model failed.")
                
    @staticmethod
    def check_columns(data, list_columns):
        """check_columns check if all needed columns for classification are in the dataframe

        Parameters
        ----------
        data : DataFrame
            input dataframe for classification
        list_columns : list
            columns to be checked

        Raises
        ------
        ValueError
            if any of the needed columns is not in the input dataframe
        """
        
        try:
            for element in list_columns:
                data[element]
        except: 
            raise ValueError(f"Please ensure that {element} column is in data.")
        return

    def predict(self, data, gaia=True):
        """predict uses pre-trained models to classify S-PLUS data

        Parameters
        ----------
        data : DataFrame
            S-PLUS data containing the features to be used in the classification
        gaia : bool, optional
            Determine if classification using GAIA features will be performed, by default True

        Returns
        -------
        DataFrame
            Contains the classification results and probabilities
        """
        if gaia:
            features = self.feat_gaia
            ypred = pd.DataFrame(self.model_gaia.predict(data[features].values))
            prob_df = pd.DataFrame(
            self.model_gaia.predict_proba(data[features].values))

        else:
            features = self.feat
            ypred = pd.DataFrame(self.model.predict(data[features].values))
            prob_df = pd.DataFrame(self.model.predict_proba(data[features].values))

        ypred.index = data.index
        results = ypred

        if self.verbose:
            print("Calculating probabilities...")

        prob_df.index = data.index
        results = pd.concat([results, prob_df], axis=1)
        
        if gaia:
            results.columns = ["CLASS_GAIA", "PROB_QSO_GAIA", "PROB_STAR_GAIA", "PROB_GAL_GAIA"]
            for col in ["PROB_QSO_GAIA", "PROB_STAR_GAIA", "PROB_GAL_GAIA"]:
                results[col] = results[col].round(3)
        else:
            results.columns = ["CLASS", "PROB_QSO", "PROB_STAR", "PROB_GAL"]
            for col in ["PROB_QSO", "PROB_STAR", "PROB_GAL"]:
                results[col] = results[col].round(3)   

        return results


    def classify(self, df, preprocess_data = True, correct_ext = True):
        """classify performs star/quasar/galaxy classification

        Parameters
        ----------
        df : DataFrame
            S-PLUS data containing the features to be used in the classification
        preprocess_data : bool, optional
            Cleans the data, by default True
        correct_ext : bool, optional
            Correct magnitudes by extinction, by default True

        Returns
        -------
        DataFrame
            Results from star/quasar/galaxy classification

        Raises
        ------
        ValueError
            if data input is empty
        """

        data = df.copy(deep=True)

        try: data.iloc[0,]
        except: raise ValueError("Data input is empty.")

        if preprocess_data:
            data = preprocess(data, correct_ext = correct_ext, value_to_insert=99)
        
        SQGClass.check_columns(data, self.feat_gaia)

        # self.results = pd.DataFrame()

        self.results_base = SQGClass.predict(self, data, gaia=False)
        self.results_gaia = SQGClass.predict(self, data, gaia=True)

        self.results = pd.concat([self.results_base, self.results_gaia], axis=1)
        if self.verbose:
            print("Finished process.")

        self.results.index = data.index
        self.results = pd.concat([data[["ID", "RA", "DEC" ]+wise+gaia], self.results], axis=1)
        return self.results.sort_index(axis=0)
