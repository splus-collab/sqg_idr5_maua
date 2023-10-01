# SQGTool DR5 - Production scripts

This repository contains scripts to be run at the Mauá server for the production phase of the star/quasar/galaxy classification for S-PLUS DR5. The training process and performance analyses are in another repository to be released within further notice.


# What is new in the latest code release?
## v0.3.0 - Sep/2023
* Environment:
    - Python 3.10.12
    - All packages were updated to the latest version for Python 3.10.12 (2021/10/21). Check file environment.yml for details.
* A new script named sqgtool.py was added. This script is the main script to be run on the Mauá server. It parses command-line arguments and calls the other scripts.
* A better logging process was added. Logs are stored in /logs/.
* Multithreading can be used for both crossmatch and classification processes. The number of threads can be set by the user.


# What is new in the analyses?

The classification for S-PLUS DR2 and DR3 follows [Nakazono et al. 2021](https://ui.adsabs.harvard.edu/abs/2021MNRAS.507.5847N/abstract). The classification for S-PLUS DR4 follows the same procedure as DR2/DR3 but with updated performance (as seen in the [documentation](https://splus.cloud/documentation/iDR4)) due to changes in reduction and calibration processes. 

The S-PLUS DR5 has further improvements in reduction and calibration processes. We made a few improvements in the classification process, briefly described below: 
 
- [Base model] Re-trained the classification model that uses S-PLUS magnitudes + WISE magnitudes + morphological parameters using the new data
- The model mentioned above also includes the objects without WISE counterparts due to increasing performance in relation to having two separate models for objects with and without WISE counterpart
- Excluded the model_flag column (due to the item above)
- Replaced ALLWISE magnitudes with unWISE magnitudes
- [GAIA model] Trained new classification model that includes GAIA parameters. We included the results in separate columns:
    - CLASS_GAIA, PROB_STAR_GAIA, PROB_QSO_GAIA, PROB_GAL_GAIA
- Included the columns from unWISE and GAIA that were used for the classification
    - W1_MAG, W2_MAG, Gmag, Plx, E(BP/RP), PM

More improvements are expected for the next months and a full documentation with code access (analyses are stored in another GitHub repository) will be prepared. 

# Column information
| Name        | Description           | 
| ------------- |:-------------| 
| ID              |  S-PLUS ID
| RA              |  Right ascension in degrees
| DEC             |  Declination in degrees
| W1_MAG          |  unWISE W1 magnitude in Vega
| W2_MAG          |  unWISE W2 magnitude in Vega
| Gmag            |  GAIA G-band mean magnitude
| Plx             |  GAIA parallax
| E(BP/RP)        |  GAIA BP/RP excess factor 
| PM              |  GAIA proper motion
| CLASS           |  Class (0= QSO, 1=STAR, 2=GALAXY) from [Base model]
| PROB_STAR       |  Probability [0,1] of a source being a star from [Base model]
| PROB_QSO        |  Probability [0,1] of a source being a quasar from [Base model]
| PROB_GAL        |  Probability [0,1] of a source being a galaxy from [Base model]
| CLASS_GAIA      |  Class (0= QSO, 1=STAR, 2=GALAXY) from [GAIA model]
| PROB_STAR_GAIA  |  Probability [0,1] of a source being a star from [GAIA model]
| PROB_QSO_GAIA   |  Probability [0,1] of a source being a quasar from [GAIA model]
| PROB_GAL_GAIA   |  Probability [0,1] of a source being a galaxy from [GAIA model]


# Performances

## [Base model]


| Metric        | QSO           | STAR  | GALAXY  |
| ------------- |:-------------:| -----:| -------:|
| Precision     | 0.930 | 0.984 | 0.972 |
| Recall        | 0.930 | 0.975 | 0.979 |
| F1            | 0.930 | 0.979 | 0.975 |

F1_weighted =  0.971



## [GAIA model]


| Metric        | QSO           | STAR  | GALAXY  |
| ------------- |:-------------:| -----:| -------:|
| Precision     | 0.939 | 0.989 | 0.981 |
| Recall        | 0.940 | 0.984 | 0.984 |
| F1            | 0.939 | 0.986 | 0.983 |

F1_weighted =  0.978

# How to run

## 1. Clone this repository
## 2. Create a conda environment

With the environment.yml file, you can create a conda environment with all the packages needed to run the scripts.

    ```
    conda env create -f environment.yml
    ```
## 3. Activate the environment
    ```
    conda activate sqg_dr5
    ```
## 4. Run the script
    ```
    python ./sqgtool.py --help
    ```

Output:
  ![SQGTool's help](https://github.com/splus-collab/sqg_idr5_maua/blob/main/help.png?raw=true)
## 5. Check the logs

Error logs for the crossmatch and classification processes are stored in /logs/ folders

# How to cite

- Please cite the original publication (S-PLUS DR2): https://ui.adsabs.harvard.edu/abs/2021MNRAS.507.5847N/abstract
- Publication for S-PLUS DR5 is in preparation. 

# Team 

This version of the star/quasar/galaxy classification was done in collaboration with (in alphabetical order):

    - Gabriel Fabiano de Souza (IAG-USP)
    - Gabriel Jacob Perin (IME-USP)
    - Pierre Ré (IAG-USP)
    - Raquel Valença (IAG-USP)
    - Vitor Cernic (IAG-USP)


# Acknowledgments 

We thank Elismar Losch for providing help with data, and Gustavo Schwarz for helping with codes and server issues 


# Report an issue

We stress that the [GAIA model] classification is still under tests by our team. Changes/improvements might be expected for this model in the near future.
If you find any problem, please open an issue in this repository or contact lilianne.nakazono at gmail dot com




