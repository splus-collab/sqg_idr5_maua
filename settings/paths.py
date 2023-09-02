import os


#%%
code_path = os.getcwd()
# print(mycwd)
os.chdir('../../..')
splus_path = os.getcwd()
# print(back_cwd)
os.chdir(code_path)
#%%

# Leave only one uncommented
#release = "iDR4"
#release = "chileanDR4"
release = "iDR5"

# VAC folder
sqg_path = os.path.join(splus_path, "Catalogues", "VACs", "sqg")
wise_path = os.path.join(sqg_path, release, "wise_match")
save_path = os.path.join(sqg_path, release)

# VAC_features folder
original_path = os.path.join(splus_path, "Catalogues", release, "dual")
correction_path = os.path.join(splus_path, "Catalogues",release, "VAC_features","corrected_sqg")
raw_path = os.path.join(splus_path, "Catalogues",release, "VAC_features","original")

# Other
# dr3_path = os.path.join(sqg_path,"DR3")
# comparison_path = os.path.join(sqg_path,"DR3xDR4")




