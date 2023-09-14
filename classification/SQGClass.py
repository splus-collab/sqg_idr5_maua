import pickle
import pandas as pd
import numpy as np
from astropy import units as u
from astroquery.utils.tap.core import TapPlus
from astropy.coordinates import SkyCoord
import requests
from settings.features import _morph, _feat

class SQGClass:
    __author__ = "Lilianne Nakazono"
    __version__ = "0.2.0"
    _pos = ["RA", "DEC"]
    _morph, _feat = _morph, _feat

    def __init__(self, model_name="", verbose=False, release="DR5", request=False):
        self.model_name = model_name
        self.verbose = verbose
        self.release = release
        
        if request:
            if self.release == "DR4":
                pass
            elif self.release == "DR5":
                pass
                # self.model = requests.get("INSERT")
            else:
                raise ValueError(
                    "Parameter release needs to be either 'DR5', 'DR4', 'DR3' or 'DR2'. Note that this package does not work for DR1 data.")
        
        else:
            if self.release == "DR4":
                with open("models/iDR4_RF_12S2W4M.sav", "rb") as f:
                    self.model = pickle.load(f)
            elif self.release == "DR5":
                pass
            else:
                raise ValueError("Try setting up request=True. request=False is only workable for DR4 and DR5.")
                
        try:
            if self.verbose:
                print("Loading model...")
            self.model = self.model.content
            self.model = pickle.loads(self.model)
        except:                 
            pass

    def irsa_query(self, data):
        '''
        NOTE: Change for unWISE
        
        Query ALLWISE catalogue from IRSA database.
        Note that this is optimized for querying per fields
        (i.e., the dataframe input must correspond to a unique field from S-PLUS)

        Keywords arguments:
        data -- dataframe containing information of RA and DEC for each object
        return dataframe containing WISE sources
        '''
        if self.verbose:
            print("Note that irsa_query() is not yet optimized for large data inputs. ",
                  "Please consider running classify() per S-PLUS field if irsa_query()=True.")
        ramin = np.min(data["RA"])
        ramax = np.max(data["RA"])
        decmin = np.min(data["DEC"])
        decmax = np.max(data["DEC"])
        col = ['ra', 'dec', 'w1mpro', 'w2mpro', 'w1snr', 'w2snr', 'w1sigmpro', 'w2sigmpro']
        if ramin < 2 and ramax > 358:
            ramax = np.max(data.query("RA<2").RA)
            ramin = np.min(data.query("RA>358").RA)
            query = f"""select {col[0]}, {col[1]}, {col[2]}, {col[3]}, {col[4]}, {col[5]}, {col[6]}, {col[7]}
            from allwise_p3as_psd
            where ra > {ramin - 0.15} or ra < {ramax + 0.15} and dec > {decmin - 0.15} and dec < {decmax + 0.15}"""
        else:
            query = f"""select {col[0]}, {col[1]}, {col[2]}, {col[3]}, {col[4]}, {col[5]}, {col[6]}, {col[7]}
            from allwise_p3as_psd
            where ra > {ramin - 0.15} and ra < {ramax + 0.15} and dec > {decmin - 0.15} and dec < {decmax + 0.15}"""

        irsa = TapPlus(url="https://irsa.ipac.caltech.edu/TAP")

        try:
            job = irsa.launch_job_async(query)
            r = job.get_results()
        except ConnectionError:
            print("Unexpected error during query.")

        df_wise = r.to_pandas()

        # Renaming any original column in data that has the same name from query
        for feat in col:
            if feat in data.columns:
                data.rename(columns={feat: feat + "_" + str(0)}, inplace=True)

        df_wise = df_wise.rename(columns={"col_0": col[0], "col_1": col[1], "col_2": col[2], "col_3": col[3],
                                          "col_4": col[4], "col_5": col[5], "col_6": col[6], "col_7": col[7]})
        return df_wise

    @staticmethod
    def crossmatch(data, df_wise):
        '''
        Perform cross match between two catalogues based on RA and DEC

        data -- S-PLUS catalogue
        df_wise -- unWISE catalogue

        NOTE: Change line below
        returns dataframe containing all original columns from data cross-matched with the ALLWISE query catalogue
        '''
        
        df_wise_temp = pd.DataFrame(columns=df_wise.columns, index=data.index)

        coo_splus = SkyCoord(data["RA"].values*u.deg, data["DEC"].values*u.deg)
        coo_wise = SkyCoord(df_wise["ra"].values*u.deg, df_wise["dec"].values*u.deg)
        idx, d2d, _ = coo_splus.match_to_catalog_sky(coo_wise)
        
        mask = d2d.arcsec <= 2
        df_wise_temp.loc[mask] = df_wise.iloc[idx[mask]].reset_index(drop=True)
        
        data['d2d'] = pd.Series(d2d.arcsec, index=data.index)
        data = pd.concat([data, df_wise_temp.reset_index(drop=True)], axis=1)

        return data

    @staticmethod
    def check_columns(data, list_columns):
        try:
            for element in list_columns:
                data[element]
        except ValueError:
            print(f"Please ensure that {element} column is in data.")
        return

    def check_match_irsa(self, data):
        '''
        Check statement of match_irsa and performs cross-match
        data -- dataframe containing S-PLUS information
        '''
        
        try:
            for element in self._pos:  # check if RA and DEC are in data to perfom the cross-match
                data[element]
        except ValueError:
            print(f"Please ensure that {element} column is in data, otherwise the cross-match with ALLWISE cannot be done.")

        if self.verbose:
            print("Querying ALLWISE catalogue via TapPlus(url='https://irsa.ipac.caltech.edu/TAP')...")

        df_wise = self.irsa_query(data)
        if self.verbose:
            print("Starting cross-match...")

        data = self.crossmatch(data, df_wise)
        return data

    def classify(self, df, return_prob=True,
                 columns_wise={'w1mpro': 'w1mpro', 'w2mpro': 'w2mpro', 'w1snr': 'w1snr',
                               'w2snr': 'w2snr', 'w1sigmpro': 'w1sigmpro', 'w2sigmpro': 'w2sigmpro'}, verbose=False):

        '''
        Create classifications for all sources

        Keywords arguments:
        df -- dataframe containing information of the 12 S-PLUS ISO magnitudes already extincted corrected
        return_prob -- if True, estimates the probabilities for each class
        
        returns a dataframe with classes
        '''

        data = df.copy(deep=True)
        self._feat_wise = [columns_wise["w1mpro"], columns_wise["w2mpro"]]

        try: data.iloc[0,]
        except: raise ValueError("Data input is empty.")

        for element in self._morph + self._feat:
            try:
                data[element]
            except:
                raise KeyError(
                    f"Please ensure that {element} column is in data. Use splusdata.connect.query() to retrieve it.")

        self.results = pd.DataFrame()

        if verbose:
            print("Note that this function assumes that the input data were previously extinction corrected. Starting classification... ")
        
        data = self.check_match_irsa(data).dropna(subset=self._morph+self._feat)
        data[self._feat_wise] = data[self._feat_wise].fillna(99)
        ypred = pd.DataFrame(self.model.predict(data[self._morph + self._feat + self._feat_wise].values))
        ypred.index = data.index
        results = ypred
        results.columns = ["CLASS"]
        
        if return_prob:
            if verbose:
                print("Calculating probabilities...")

            prob_df = pd.DataFrame(
                self.model.predict_proba(data[self._morph + self._feat + self._feat_wise].values))
            prob_df.index = data.index
            results = pd.concat([results, prob_df], axis=1)
            results.columns = ["CLASS", "PROB_QSO", "PROB_STAR", "PROB_GAL"]

        if verbose:
            print("Finished process.")

        return results.sort_index(axis=0)
