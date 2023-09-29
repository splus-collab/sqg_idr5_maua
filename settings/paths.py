import os

# Leave only one uncommented
# release = "iDR5"
release = "CHANCES_XPSP_GAIA"
# release = "CHANCES_XPSP"


splus_path = os.path.join(os.path.sep,"storage","splus")
code_path = os.path.join(os.path.sep, "storage", "splus", "scripts", "sqg_idr5")

# Dustmaps
dustmap_path = os.path.join(code_path, "dustmaps")

# VAC folder
sqg_path = os.path.join(splus_path, "Catalogues", "VACs", "sqg")
wise_path = os.path.join(sqg_path, release, "wise_match")
gaia_wise_path = os.path.join(sqg_path, release, "gaia_wise_match")
original_path = os.path.join(sqg_path, release, "original")
output_path = os.path.join(sqg_path, release, "final_output")
log_path = os.path.join(os.path.join(code_path, "logs"))



