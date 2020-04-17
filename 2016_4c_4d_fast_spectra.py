import pathlib
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker
import numpy as np

import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

### These payloads did not see much ###

save_fig = False
fs_path = pathlib.Path('merged_data', 'barrel_4c_4d_merged_fast_spectra.csv')
ephem_dir = pathlib.Path('merged_data', 'barrel_4c_4d_merged_ephemeris.csv')

fs = pd.read_csv(fs_path, index_col=0)
fs.index = pd.to_datetime(fs.index)
print(fs.head())

ephem = pd.read_csv(ephem_dir, index_col=0)
ephem.index = pd.to_datetime(ephem.index)
print(ephem.head())

# Filter the fast spectra
filtered_fs = fs['2016/08/22T05:00:00':'2016/08/22T13:00:00']

if filtered_fs.shape[0] > 100_000:
    # Downsample to make plotting faster
    filtered_fs = filtered_fs.loc[::filtered_fs.shape[0]//100_000]

### PLOT THE ZOOMED OUT SUMMARY PLOT ###
fig, bx = plt.subplots(2, 1, sharex=True, figsize=(10, 5))

for column in filtered_fs.columns:
    if '4C' in column: 
        plt_num=0
    else:
        plt_num=1
    bx[plt_num].plot(filtered_fs.index, filtered_fs[column], label=column)

bx[0].legend(loc=1)
bx[1].legend(loc=1)

plt.show()