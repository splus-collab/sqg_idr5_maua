from classification.SQGClass import SQGClass
import glob
import os
from settings.paths import *
import logging
import pandas as pd
from tqdm import tqdm
from astropy.table import Table
# from settings.features import morph, splus, wise
import sys
import traceback
import warnings
# from astropy.utils.exceptions import AstropyUserWarning

warnings.filterwarnings("ignore")

# note: To run the code in my computer, I've created "input", "ouput", and "models" folders inside the repository
# I've also moved this file outside the "classification" folder
# wise_path = "input"
# save_path = "output"

logging.basicConfig(filename=os.path.join("logs", "classification.log"),
                    format='%(asctime)s: %(levelname)s: %(message)s',  filemode='w', level=logging.ERROR)

file_list = glob.glob(os.path.join(gaia_wise_path, "*"))
model = SQGClass()

with tqdm(position=0, leave=True) as pbar:
    for filename in tqdm(file_list):
        a = 0
        if a == 1:
            pass

        # if os.path.exists(os.path.join(save_path,filename.split('/')[-1])):         
        #     continue

        else:
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
                # print(f"ERROR ON CLASSIFICATION FOR {filename}")
                with open(os.path.join(log_path,'filename_error_classification.txt'), 'w') as f:
                    f.write(filename)
            else:
                # results.index = data.index
                # results = pd.concat([data[["ID", "RA", "DEC"]], results], axis=1)
                # results.to_csv(os.path.join(save_path,filename.split('/')[-1]), sep =",", index=False)
                # results = Table.from_pandas(results)
                results.to_csv(os.path.join(output_path, filename.split(os.path.sep)[-1].split('.')[0]+".csv"), index=False, sep=",")
