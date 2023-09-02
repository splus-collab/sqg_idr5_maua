import os
import pandas as pd
from utils.sfdmap import SFDMap
import extinction
from utils.paths import data_path
import numpy as np
from utils.columns import feat, wise, sdss

def correction(data, aper, splus_bands = True, sdss_bands = True, wise_bands = True):
    chunk = data.copy(deep=True)
    splus = [item+"_"+aper for item in feat]
    # feat = galex+splus+wise
    features = []
    all_lambdas = []
    m = SFDMap(os.path.join(data_path, 'dustmaps'))
    EBV = m.ebv(chunk.RA, chunk.DEC)

    # Obtendo A_v nesta mesma posição
    AV  = m.ebv(chunk.RA, chunk.DEC)*3.1

    if splus_bands:
    # Calculando a extinção em outros comprimentos de onda
    # Utilizando a lei de extinção de Cardelli, Clayton & Mathis.
        Lambdas_splus = np.array([3536, 3770, 3940, 4094, 4292, 4751, 5133, 6258, 6614, 7690, 8611, 8831])
        features.append(splus)
        all_lambdas.append(Lambdas_splus)
    if wise_bands:
        Lambdas_wise = np.array([33526.00, 46028.00])
        features.append(wise)
        all_lambdas.append(Lambdas_wise)
    if sdss_bands:
        Lambdas_sdss = np.array([3543, 4770, 6231, 7625, 9134])
        features.append(sdss)
        all_lambdas.append(Lambdas_sdss)

    all_lambdas = np.concatenate(all_lambdas)
    features = np.concatenate(features)
    
    Extinctions = []
    for i in range(len(AV)):
        Extinctions.append(extinction.ccm89(all_lambdas, AV[i], 3.1))

    Extinction_DF = pd.DataFrame(Extinctions, columns=features)
    chunk = chunk.reset_index(drop=True)

    mask_99 = chunk[features]==99
    chunk[features] = chunk[features].sub(Extinction_DF)
    chunk[features] = chunk[features].mask(mask_99, other = 99)
    return chunk

