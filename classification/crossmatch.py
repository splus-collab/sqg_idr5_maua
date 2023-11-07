import sys
sys.path.append('/storage/splus/scripts/sqg_idr5/settings')
sys.path.append('/storage/splus/scripts/sqg_idr5/')

import os
import logging
from settings.paths import  log_path
import logging
import glob 
import subprocess
import datetime
from utils.multithread import run_multithread


dt = datetime.datetime.now()
dt = dt.strftime("%Y-%m-%d_%H-%M")

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=os.path.join(log_path,f"match_{dt}.log"),format='%(asctime)s:     %(levelname)s: %(message)s',  filemode='w', level=0)
logging.info("Crossmatching with WISE and GAIA")


def unwise_gaia_cdsxmatch(file_list, output_folder, replace=False, verbose=True):
    wise_path = os.path.join(output_folder, "wise_match")
    gaia_wise_path = os.path.join(output_folder, "gaia_wise_match")

    for filename in file_list:
        field = filename.split(os.path.sep)[-1].split('_dual')[0]
        if verbose:
            print('Starting '+f'{field}')

        skip_wise = False
        skip_gaia = False
        if os.path.exists(os.path.join(wise_path, field)+".fits") and replace==False:
            skip_wise = True
        if os.path.exists(os.path.join(gaia_wise_path, field)+".fits") and replace==False:
            skip_gaia = True

        if skip_wise == False:
            cmd = [
                "java", "-jar", "stilts.jar", "cdsskymatch",
                f"in={filename}",
                "cdstable=II/363/unwise", "ra=RA", "dec=DEC", "radius=2",
                "find=each", "blocksize=100000",
                f"out={os.path.join(wise_path, field)}.fits"]

            # Fazendo o cross-match com o unWISE.
            # os.system(f"""java -jar stilts.jar cdsskymatch in={filename}  cdstable=II/363/unwise ra=RA dec=DEC radius=2 find=each blocksize=100000  ocmd='delcols "XposW1 XposW2 YposW1	YposW2 e_XposW1	e_XposW2 e_YposW1 e_YposW2 rchi2W1 rchi2W2 FW1lbs FW2lbs e_FW1lbs e_FW1lbs fwhmW1 fwhmW2 SpModW1 SpModW2 e_SpModW1 	e_SpModW2 skyW1	skyW2 RAW1deg RAW2deg DEW1deg DEW2deg coaddID detIDW1 detIDW2 nmW1 nmW2 PrimW1 PrimW2 FlagsW1 FlagsW2 f_FlagsW1	f_FlagsW2 Prim"' out={os.path.join(wise_path, field)}.fits""")
            try:
                result = subprocess.run(cmd, capture_output=True, check=True)
            except:
                pass
            if os.path.exists(os.path.join(wise_path, field)+".fits")==False:
                logging.error("%s" %(field))
                with open(os.path.join(log_path, f'filename_error_crossmatch_{dt}.txt'), 'a') as f:
                    f.write(filename+"\n")

        if skip_gaia == False:
            cmd = [
                "java", "-jar", "stilts.jar", "cdsskymatch",
                f"in={os.path.join(wise_path, field)}.fits",
                "cdstable=I/355/gaiadr3", "ra=RA", "dec=DEC", "radius=1",
                "find=each", "blocksize=100000",
                f"out={os.path.join(gaia_wise_path, field)}.fits"]

            # # Fazendo o cross-match com o GAIA.
            try:
                result = subprocess.run(cmd, capture_output=True, check=True)
            except:
                pass
            if os.path.exists(os.path.join(gaia_wise_path, field)+".fits")==False:
                logging.error("%s" %(field))
                with open(os.path.join(log_path, f'filename_error_crossmatch_{dt}.txt'), 'a') as f:
                    f.write(filename+"\n")


if __name__=="__main__":
    file_list = glob.glob(os.path.join(original_path, "*.fits"))
    run_multithread(file_list, unwise_gaia_cdsxmatch, output_folder = output_folder, Num_Parallel=30, replace=False, verbose=True)