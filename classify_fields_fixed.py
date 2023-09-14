from classification.SQGClass import SQGClass
import glob
import os
# from settings.paths import save_path, wise_path
import logging
import pandas as pd
from tqdm import tqdm
from astropy.table import Table
from settings.features import _morph, _feat

# NOTE: To run the code in my computer, I've created "input", "ouput", and "models" folders inside the repository
# I've also moved this file outside the "classification" folder
wise_path = "input"
save_path = "output"

logging.basicConfig(filename=os.path.join(save_path, "classification.log"),
                    format='%(asctime)s: %(levelname)s: %(message)s',  filemode='w', level=logging.DEBUG)

file_list = glob.glob(os.path.join(wise_path, "*"))

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
                data = data.to_pandas().dropna(subset=_morph+_feat)
                data["ID"] = data["ID"].str.decode('utf-8')
                data.rename(
                    columns={"W1mag": "w1mpro", "W2mag": "w2mpro", "e_W1mag": "w1sigmpro", "e_W2mag": "w2sigmpro"},
                    inplace=True)                   
                results = model.classify(data)
                
            except Exception as e:
                print(e)
                logging.error(f"{filename}: ERROR ON CLASSIFICATION")
                print(f"ERROR ON CLASSIFICATION FOR {filename}")

            else:
                results.index = data.index
                results = pd.concat([data[["ID", "RA", "DEC"]], results], axis=1)
                # results.to_csv(os.path.join(save_path,filename.split('/')[-1]), sep =",", index=False)
                results = Table.from_pandas(results)
                results.write(os.path.join(save_path, filename.split(os.path.sep)[-1]), overwrite=True)
