# barrel_proximity_flights

This repository looks at data taken by pairs of BARREL balloon 
payloads in proximity during the 2015 and 2016 Sweden campaigns.
The scripts in ```other_flights/``` folder analyzed the data 
from the 2016 BARREL campaigns. Unfortinately only payloads 4c and 
4d took data togeather and did not observe anything interesting.

## Project Structure (rerun ```tree -a -I "*png|*pdf|*pyc|.git"```)
```
├── 2015_3g_3f_data_preprocessing.py - Processes the 2015 ballon flight cdfs
├── 2015_3g_3f_fast_spectra.py - Handles the fast spectra summary plots
├── 2015_3g_3f_trajectory.py - Plots the payload trajectories, altitudes, and separation
├── data_preprocessing.py - Merges and cleans the cdf files into csv files.
├── directories.py - Contains the one hard-coded directory to the data.
├── .gitignore - Ignores __pycache__, plots, and data (to keep the repo small)
├── .ipynb_checkpoints
│   ├── barrel_3g_3f_trajectory-checkpoint.ipynb
│   └── plotly_map-checkpoint.ipynb
├── merged_data - Contains the merged fast spectra and ephemeris csv files.
├── other_flights - Old scripts to look at other flights that did not lead anywhere.
├── plots - Summary plots for various durations.
│   ├── 15min
│   ├── 2min
│   └── 5min
├── presentations
│   └── 20200415_barrel_3g_3f_microbursts.pptx
├── __pycache__
├── README.md
└── .vscode - Contains Python tasks and other settings for VS Code IDE.
    ├── settings.json
    └── tasks.json
```