aper="iso"
morph = ['FWHM_n', 'A', 'B', 'KRON_RADIUS']
broad = [mag+"_"+aper for mag in ('u', 'g', 'r', 'i', 'z')]
narrow = [mag+"_"+aper for mag in ('J0378', 'J0395', 'J0410', 'J0430', 'J0515', 'J0660', 'J0861')]
splus = broad+narrow
wise = ["W1_MAG", "W2_MAG"]
gaia_mag, gaia_param = ['Gmag'], ['Plx', 'E(BP/RP)', 'PM']
gaia = gaia_mag + gaia_param