import os
from glob import glob
from tqdm import tqdm

chances_path = "/storage/splus/Catalogues/CHANCES"

list_folders = glob(os.path.join(chances_path, "*"))


for folder in tqdm(list_folders):
    file = os.path.join(folder, "dual", "*VAC*.fits")
    os.system(f'''cp {file} /storage/splus/Catalogues/VACs/sqg/CHANCES_sep23/original/''')