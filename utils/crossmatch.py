import pandas as pd
import numpy as np
import os
import time
import logging
import threading
from tqdm import tqdm # Progress bar
from settings.paths import wise_path,save_path, correction_path
import logging
import glob 

logging.basicConfig(filename=os.path.join(save_path,"match-wise.log"),format='%(asctime)s:     %(levelname)s: %(message)s',  filemode='w', level=logging.DEBUG)

file_list = glob.glob(os.path.join(correction_path, "*.csv"))

# All_Fields        = pd.read_csv('S82_Fields.csv') # All fields to be downloaded
# Fields_Downloaded = [s.replace('.csv', '') for s in os.listdir(wise_path) if s.endswith('.csv') and not s.startswith('S82_F')] # Fields already downloaded
# Field_List        = np.setdiff1d(All_Fields, Fields_Downloaded) # If there are fields that still need to be downloaded, they will be on this list
# Field_List        = pd.DataFrame(Field_List, columns=['Field'])

def thread_function(file_list):
    for filename in file_list:
        field = filename.split(os.path.sep)[-1].split('_')[0]
        print('Starting '+f'{field}')
        print(filename)
        try:
            # Fazendo o cross-match com o 2MASS, GALEX e o unWISE.
            os.system(f"""java -jar stilts.jar cdsskymatch in={filename}  cdstable=II/328/allwise ra=RA dec=DEC radius=2 find=each blocksize=100000  ocmd='delcols "eeMaj eeMin eePA W3mag W4mag Jmag Hmag Kmag e_W3mag e_W4mag e_Jmag e_Hmag e_Kmag ccf ex var qph pmRA e_pmRA pmDE e_pmDE d2M"' out={os.path.join(wise_path, field)}.fits""")
        # If a given field could not be downloaded for some reason, this code will write it to a file.
        # The way this is coded allows you to just change the 'Field_List' below to use the Error_Fields.csv file and try downloading these fields again
        except:
            logging.error("%s: ERROR on WISE crossmatch" %field)
            print(f"Error on {field}")

# To speed-up the download of data we use multithreading.
# In this example, the field list is split into 10 parts and each part is processed using a different thread. This way we can download 10 fields in parallel
# You may need to adapt this code by changing the "Num_Threads" and removing/adding a few 'process_x' lines below.
Num_Parallel = 3 # The number of files downloaded in parallel (but sometimes it will download this number -1)
Threads = np.arange(0, len(file_list)+1, 1) # The number of threads (each thread will be used to download a field)

print('# Number of fields:', len(file_list))
print('# Number of simultaneous downloads:', Num_Parallel)

# Create a dictionary to store the processes (threads)
Processes = {}

# Populating the dictionary with the processes (one thread per item of the dictionary, each thread downloads a field)
for i in range(len(Threads)-1):
    Processes[i] = threading.Thread(target=thread_function, args=(file_list[Threads[i]: Threads[i+1]],))

# Starting the threads (downloading 5 at a time to not overload the cloud)
for list_of_fields in np.array_split(np.arange(0, len(Threads)-1), np.ceil(len(Threads)/Num_Parallel)):
    print('# Starting threads:', list_of_fields)
    for i in list_of_fields:
        Processes[i].start()
        time.sleep(1.5)

    for i in list_of_fields:
        Processes[i].join()
    print('# Finished threads:', list_of_fields)
    print()
