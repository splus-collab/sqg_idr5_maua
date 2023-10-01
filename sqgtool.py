import os
import argparse
from glob import glob
from classification.crossmatch import unwise_gaia_cdsxmatch
from classification.classify_fields import classify_fields
from utils.multithread import run_multithread

def parse_args():
    """
    This function parses the arguments passed to the script.
    
    Returns args
    """

    parser=argparse.ArgumentParser(description="This script runs the star/quasar/galaxy classification for the S-PLUS fields (DR5). \n This script should not be run in fields that were already corrected by extinction. Please run it in the original files.")
    parser.add_argument('--input_folder', 
                        metavar="-i", 
                        help='This folder should contain the .fits files for the S-PLUS fields to be classified')
    
    parser.add_argument('--output_folder', 
                        metavar="-o", 
                        required=True,  
                        help='Folder to save the VAC output files. By default, VAC output will be saved under [output_folder]/final_output/')
    
    parser.add_argument('--crossmatch', 
                        default = False,
                        dest="crossmatch",
                        action="store_true",
                        help='Crossmatch files with unWISE and GAIA. By default, crossmatch files will be saved under [output_folder]/wise_match/ and [output_folder]/gaia_wise_match/')
    
    parser.add_argument('--no-crossmatch', 
                        dest="crossmatch",
                        action="store_false",
                        help='Skips crossmatching process.')
    
    parser.add_argument('--n_threads', 
                        default = 0,
                        choices = range(2, 31),
                        type = int,
                        help='Defines number of thread processes. Default is 0, which means it will not run in multithreads.')
    
    parser.add_argument('--replace_crossmatch',
                        default = False,
                        dest="replace_crossmatch",
                        action="store_true",
                        help='Replace crossmatch files if they exist'
                        )
    
    parser.add_argument('--no-replace_crossmatch',
                        dest="replace_crossmatch",
                        action="store_false",
                        help='Does not replace crossmatch files if they exist '
                        )
    
    parser.add_argument('--replace_vac',
                        default = False,
                        dest="replace_vac",
                        action="store_true",
                        help='Replace VAC files if they exist'
                        )
    
    parser.add_argument('--no-replace_vac',
                        dest="replace_vac",
                        action="store_false",
                        help='Does not VAC files if they exist'
                        )
    parser.add_argument('--diff',
                        default = False,
                        action="store_true",
                        help='Check only files that are in the input folder but are not in the vac folder'
                        )
    
    parser.add_argument('--verbose', 
                        default = True,
                        dest="verbose",
                        action="store_true",
                        help='Turns on prints throughout the processes.') 
    
    parser.add_argument('--no-verbose', 
                        dest="verbose",
                        action="store_true",
                        help='Turns off prints throughout the processes.') 
    args = parser.parse_args()
    return args

def create_folder(path):
    """create_folder check if folder exists, if not, creates it

    Parameters
    ----------
    path : string

    """

    if not os.path.exists(path):
        os.makedirs(path)

def define_paths(args):
    """define_paths define subfolders that will be created within this script

    Parameters
    ----------
    args : parsed with parse_args()

    Returns
    -------
    vac_output : string
        path to final_output folder where the VAC files will be saved
    wise_output : string
        path to wise_match folder
    gaia_wise_output : string
        path to gaia_wise_match folder
    """
    vac_output = os.path.join(args.output_folder, "final_output")
    wise_output = os.path.join(args.output_folder, "wise_match")
    gaia_wise_output = os.path.join(args.output_folder, "gaia_wise_match")

    for path in [vac_output, wise_output, gaia_wise_output]:
        create_folder(path) #creates folder if it doesnt exist

    return vac_output, wise_output, gaia_wise_output

def missing_fields(input,vac_output):
    list_input = os.listdir(input)
    list_output = os.listdir(vac_output)
    list_input = [x.split('_dual')[0].split('.')[0] for x in list_input]
    list_output = [x.split('.')[0] for x in list_output]
    missing = list(set(list_input)-set(list_output))
    # print(missing)
    missing = [x.split(".fits")[0]+"_dual_VAC_features.fits" for x in missing]
    print(missing)
    return missing

def main(args):
    """main performs crossmatchs, preprocessing and classification for S-PLUS fields

    Parameters
    ----------
    args : parsed with parse_args()

    """

    vac_output, wise_output, gaia_wise_output = define_paths(args)
    if args.diff:
        # only runs classification for files that are in the input folder but are not in the vac folder
        missing = missing_fields(args.input_folder,vac_output)
        file_list = [os.path.join(args.input_folder,field) for field in missing]
    else:
        # run classification for all files in folder
        file_list = glob(os.path.join(gaia_wise_output, "*.fits"))
    
    if args.crossmatch:
        unwise_gaia_cdsxmatch(file_list, output_folder=args.output_folder,  replace=args.replace_crossmatch, verbose=args.verbose)
    

    if args.n_threads > 0:
        run_multithread(file_list, function=classify_fields,  Num_Parallel=args.n_threads, output_folder=vac_output, replace=args.replace_vac, verbose=args.verbose)
    else:
        classify_fields(file_list, output_path=vac_output, replace=args.replace_vac, verbose=args.verbose)

if __name__=="__main__":
    args = parse_args()
    main(args)