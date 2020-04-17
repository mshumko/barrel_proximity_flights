import pathlib
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker

import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

save_fig = False
data_dir = pathlib.Path('merged_data', 'barrel_3g_3f_merged_ephemeris.csv')

ephem = pd.read_csv(data_dir, index_col=0)
ephem.index = pd.to_datetime(ephem.index)
print(ephem.head())

# Downsample ephemeris for plotting
n_plot = 100
ephem_downsampled = ephem.iloc[::ephem.shape[0]//n_plot]

# Create a color map
sm = plt.cm.ScalarMappable(cmap='viridis', 
                           norm=plt.Normalize(vmin=ephem.index.min().value,
                                              vmax=ephem.index.max().value))
fig, ax = plt.subplots(1, 3, figsize=(15, 5))
sc = ax[0].scatter(ephem_downsampled['3G_GPS_Lon'], ephem_downsampled['3G_GPS_Lat'], 
                    c=ephem_downsampled.index, marker='o', s=50, alpha=0.5, label='3G')
ax[0].scatter(ephem_downsampled['3F_GPS_Lon'], ephem_downsampled['3F_GPS_Lat'], 
                    c=ephem_downsampled.index, marker='s', s=50, alpha=0.5, label='3F')
cbar = plt.colorbar(sm, ax=ax[0], label='Time [MM/DD HH]')
# Change the numeric ticks into ones that match the x-axis
cbar.ax.set_yticklabels(pd.to_datetime(cbar.get_ticks()).strftime(date_format='%m/%d %H'))

ax[1].plot(ephem_downsampled.index, ephem_downsampled['3G_GPS_Alt'], label='3G')
ax[1].plot(ephem_downsampled.index, ephem_downsampled['3F_GPS_Alt'], label='3F')
             
ax[2].plot(ephem_downsampled.index, ephem_downsampled['dist_km'])

ax[0].set(title=f'BARREL 3G and 3F trajectories', 
          xlabel='Lon', ylabel='Lat')
ax[1].set(title=F'BARREL 3G and 3F Altitude', ylabel='Altitude [km]',
          xlabel=f'UTC', ylim=(20, None))
ax[2].set(title=F'BARREL 3G and 3F Separation', ylabel='Separation [km]',
          xlabel=f'UTC')

# Format ax[1] and ax[2] x axis
time_fmt = matplotlib.dates.DateFormatter('%m/%d %H')
for a in ax[1:]:
    a.xaxis.set_major_formatter(time_fmt)
    a.xaxis.set_major_formatter(time_fmt)
    a.xaxis.set_minor_locator(matplotlib.dates.HourLocator(interval=1))
    a.xaxis.set_major_locator(matplotlib.dates.HourLocator(interval=6))

ax[0].legend()
ax[1].legend()

plt.tight_layout()

if save_fig:
    plt.savefig('20150825_BARREL_3G_3F_trajectories.pdf')
plt.show()