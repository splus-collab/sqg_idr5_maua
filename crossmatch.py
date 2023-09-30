import pandas as pd
import numpy as np
import os
import time
import logging
import threading
from tqdm import tqdm # Progress bar
from settings.paths import wise_path,original_path, log_path, gaia_wise_path
import logging
import glob 
import subprocess

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=os.path.join(log_path,"match.log"),format='%(asctime)s:     %(levelname)s: %(message)s',  filemode='w', level=0, force=True)
logging.info("Crossmatching with WISE and GAIA")

file_list = glob.glob(os.path.join(original_path, "*.fits"))

def thread_function(file_list):
    for filename in file_list:
        field = filename.split(os.path.sep)[-1].split('_dual')[0]
        print('Starting '+f'{field}')
        
        # cmd = [
        #     "java", "-jar", "stilts.jar", "cdsskymatch",
        #     f"in={filename}",
        #     "cdstable=II/363/unwise", "ra=RA", "dec=DEC", "radius=2",
        #     "find=each", "blocksize=100000",
        #     f"out={os.path.join(wise_path, field)}.fits"]

        # # Fazendo o cross-match com o unWISE.
        # # os.system(f"""java -jar stilts.jar cdsskymatch in={filename}  cdstable=II/363/unwise ra=RA dec=DEC radius=2 find=each blocksize=100000  ocmd='delcols "XposW1 XposW2 YposW1	YposW2 e_XposW1	e_XposW2 e_YposW1 e_YposW2 rchi2W1 rchi2W2 FW1lbs FW2lbs e_FW1lbs e_FW1lbs fwhmW1 fwhmW2 SpModW1 SpModW2 e_SpModW1 	e_SpModW2 skyW1	skyW2 RAW1deg RAW2deg DEW1deg DEW2deg coaddID detIDW1 detIDW2 nmW1 nmW2 PrimW1 PrimW2 FlagsW1 FlagsW2 f_FlagsW1	f_FlagsW2 Prim"' out={os.path.join(wise_path, field)}.fits""")
        # result = subprocess.run(cmd, capture_output=True, check=True)
        # if "Failed" in str(result):
        #     logging.error("%s: %s" %(field, result))
        # # print(f"Error on {field}")

        cmd = [
            "java", "-jar", "stilts.jar", "cdsskymatch",
            f"in={os.path.join(wise_path, field)}.fits",
            "cdstable=I/355/gaiadr3", "ra=RA", "dec=DEC", "radius=1",
            "find=each", "blocksize=100000",
            f"out={os.path.join(gaia_wise_path, field)}.fits"]

        # # Fazendo o cross-match com o GAIA.
        result = subprocess.run(cmd, capture_output=True, check=True)
        if "Failed" in str(result):
            logging.error("%s: %s" %(field, result))

# To speed-up the download of data we use multithreading.
# In this example, the field list is split into 10 parts and each part is processed using a different thread. This way we can download 10 fields in parallel
# You may need to adapt this code by changing the "Num_Threads" and removing/adding a few 'process_x' lines below.
Num_Parallel = 10 # The number of files downloaded in parallel (but sometimes it will download this number -1)
Threads = np.arange(0, len(file_list)+1, 1) # The number of threads (each thread will be used to download a field)

print('# Number of fields:', len(file_list))
print('# Number of simultaneous downloads:', Num_Parallel)

# Create a dictionary to store the processes (threads)
Processes = {}

# Populating the dictionary with the processes (one thread per item of the dictionary, each thread downloads a field)
for i in range(len(Threads)-1):
    Processes[i] = threading.Thread(target=thread_function, args=(file_list[Threads[i]: Threads[i+1]],))

# Starting the threads (downloading 5 at a time to not overload the cloud)
i=Num_Parallel
for list_of_fields in np.array_split(np.arange(0, len(Threads)-1), np.ceil(len(Threads)/Num_Parallel)):
    print('# Starting threads:', list_of_fields)
    for i in list_of_fields:
        Processes[i].start()
        time.sleep(1.5)

    for i in list_of_fields:
        Processes[i].join()
    print('# Finished threads:', list_of_fields)

    print('%s/%s' %(i, len(file_list)))
    i=i+Num_Parallel
    print()
