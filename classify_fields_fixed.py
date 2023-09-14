from classification.SQGClass import SQGClass
import glob
import os
#from paths import save_path, wise_path
import logging
import pandas as pd
from tqdm import tqdm
from astropy.table import Table
from settings.features import _morph, _feat

wise_path = "input"
save_path = "output"

logging.basicConfig(filename=os.path.join(save_path, "classification.log"),
                    format='%(asctime)s: %(levelname)s: %(message)s',  filemode='w', level=logging.DEBUG)

# _morph = ['FWHM_n', 'A', 'B', 'KRON_RADIUS']
# _feat = ['u_iso',
#       'J0378_iso',
#       'J0395_iso',
#       'J0410_iso',
#       'J0430_iso',
#       'g_iso',
#       'J0515_iso',
#       'r_iso',
#       'J0660_iso',
#       'i_iso',
#       'J0861_iso',
#       'z_iso']


file_list = glob.glob(os.path.join(wise_path, "csv"))

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
                #data = pd.read_table(filename, sep=",")
                data = Table.read(filename, format="fits")
                data = data.to_pandas()
                data["ID"] = data["ID_in"].str.decode('utf-8')
                data.rename(columns={"W1mag": "w1mpro", "W2mag": "w2mpro", "e_W1mag": "w1sigmpro", "e_W2mag": "w2sigmpro"},
                            inplace=True)

                #col_wise = {"w1mpro":"W1mag", "w2mpro":"W2mag", "w1sigmpro": "e_W1mag", "w2sigmpro": "e_W2mag"}                    

                results = model.classify(data)
            except Exception as e:
                print(e)
                logging.error("%s : ERROR ON CLASSIFICATION" %filename)
                print(f"ERROR ON CLASSIFICATION FOR {filename}")

            else:
                results.index = data.index
                results = pd.concat([data[["ID", "RA", "DEC"]], results], axis=1)
                #results.to_csv(os.path.join(save_path,filename.split('/')[-1]), sep =",", index=False)
                results = Table.from_pandas(results)
                results.write(os.path.join(save_path, filename.split(os.path.sep)[-1]), overwrite=True)
