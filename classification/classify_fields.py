import glob
import os
import logging
from astropy.table import Table
import traceback
import warnings
import datetime
from utils.multithread import run_multithread
# from settings.paths import gaia_wise_path, log_path, output_path
from classification.SQGClass import SQGClass
from settings.paths import log_path
from tqdm import tqdm 

warnings.filterwarnings("ignore")

dt = datetime.datetime.now()
dt = dt.strftime("%Y-%m-%d_%H-%M")
logging.basicConfig(filename=os.path.join("logs", f"classification_{dt}.log"),
                    format='%(asctime)s: %(levelname)s: %(message)s',  filemode='w', level=logging.ERROR)

# release="CHANCES_XPSP_GAIA_BR"

# splus_path = os.path.join(os.path.sep,"storage","splus")
# code_path = os.path.join(os.path.sep, "storage", "splus", "scripts", "sqg_idr5")

# # Dustmaps
# dustmap_path = os.path.join(code_path, "dustmaps")

# # VAC folder
# sqg_path = os.path.join(splus_path, "Catalogues", "VACs", "sqg")
# wise_path = os.path.join(sqg_path, release, "wise_match")
# gaia_wise_path = os.path.join(sqg_path, release, "gaia_wise_match")
# original_path = os.path.join(sqg_path, release, "original")
# output_path = os.path.join(sqg_path, release, "final_output")
# log_path = os.path.join(os.path.join(code_path, "logs"))


def classify_fields(file_list, output_path, replace=False, verbose=True):
    model = SQGClass()
    for filename in tqdm(file_list):
        output_filename = filename.split(os.path.sep)[-1].split('.')[0]+".csv"
        if verbose:
            print(output_filename)

        skip_classification = False
        if os.path.exists(os.path.join(output_path,output_filename)):
            if replace == False:
                skip_classification = True
            else:
                skip_classification = False

        if skip_classification  == False:
            try:
                # data = pd.read_table(filename, sep=",")
                data = Table.read(filename, format="fits")
                # data = data.to_pandas().dropna(subset=morph+splus+wise)
                data = data.to_pandas()
                data["ID"] = data["ID"].apply(lambda x: x.decode('utf-8')) 
                results = model.classify(data, preprocess_data=True, correct_ext=True)
                
            except Exception as e:
                print(e)
                logging.error(f"{filename.split(os.path.sep)[-1]}: error on classification")
                logging.error(e)
                print(traceback.format_exc())
                with open(os.path.join(log_path, f'filename_error_classification_{dt}.txt'), 'a') as f:
                    f.write(filename)
            else:
                results.to_csv(os.path.join(output_path, output_filename), index=False, sep=",")


# if __name__ == "__main__":
    # file_list = glob.glob(os.path.join(gaia_wise_path, "*"))
    # run_multithread(file_list, classify_fields, Num_Parallel=10, replace=False, verbose=True)