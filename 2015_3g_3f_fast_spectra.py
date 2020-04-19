import pathlib
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker
import numpy as np

import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

save_fig = False
fs_path = pathlib.Path('merged_data', 'barrel_3g_3f_merged_fast_spectra.csv')
ephem_dir = pathlib.Path('merged_data', 'barrel_3g_3f_merged_ephemeris.csv')

fs = pd.read_csv(fs_path, index_col=0, parse_dates=True)
# fs.index = pd.to_datetime(fs.index)
print(fs.head())

ephem = pd.read_csv(ephem_dir, index_col=0, parse_dates=True)
# ephem.index = pd.to_datetime(ephem.index)
print(ephem.head())

# Filter the fast spectra
filtered_fs = fs['20150825T09:00:00':'20150826T9:00:00']

if filtered_fs.shape[0] > 100_000:
    # Downsample to make plotting faster
    filtered_fs = filtered_fs.loc[::filtered_fs.shape[0]//100_000]

### PLOT THE ZOOMED OUT SUMMARY PLOT ###
fig, bx = plt.subplots(2, 1, sharex=True, figsize=(10, 5))

for column in filtered_fs.columns:
    if '3G' in column: 
        plt_num=0
    else:
        plt_num=1
    bx[plt_num].plot(filtered_fs.index, filtered_fs[column], label=column)

bx[0].legend(loc=1)
bx[1].legend(loc=1)

# def onMouseMove(event):
#     """
#     Draw vertical line through both subplots.
#     """
#     bx[0].lines = bx[0].lines[:-1]
#     bx[1].lines = bx[1].lines[:-1]
#     bx[0].axvline(x=event.xdata, color="k")
#     bx[1].axvline(x=event.xdata, color="k")
#     return

# fig.canvas.mpl_connect('motion_notify_event', onMouseMove)

# plt.savefig('20150825_BARREL_3G_3F_fast_spectra.pdf')

### MAKE NARROWER SUMMARY PLOTS ###

xlabel_variables = ['3G_L_Kp2', '3G_MLT_Kp2_T89c', '3G_GPS_Alt', '3F_GPS_Alt', 'dist_km']

def xlabel_func(i):
    date = str(ephem.index[i].date())
    time = str(ephem.index[i].strftime("%H:%M:%S"))
    aux_vals_list = list(ephem.loc[ephem.index[i], xlabel_variables].round(1).values.flatten()
                            )
    aux_vals_str = str(aux_vals_list).replace(', ', '\n').replace('[', '').replace(']', '')
    return (date + '\n' + time + '\n' + aux_vals_str)

def format_fn(tick_val, tick_pos):
    """
    The tick magic happens here. pyplot gives it a tick time, and this function 
    returns the closest label to that time. Read docs for FuncFormatter().
    """
    numeric_time = matplotlib.dates.date2num(ephem.index)
    idx = np.argmin(np.abs(numeric_time-tick_val))
    return xlabel_func(idx)


time_freq = '2min'

if not pathlib.Path('plots', time_freq).is_dir():
    pathlib.Path('plots', time_freq).mkdir(parents=True, exist_ok=True)
    print(f'Made a plots/{time_freq}/ directory')

times = pd.date_range('20150826T04:30:00', '20150826T08:25:00', freq=time_freq)
fig, cx = plt.subplots(2, 1, sharex=True, figsize=(10, 5), sharey=True)

for start_time, end_time in zip(times[:-1], times[1:]):
    filtered_fs = fs[start_time:end_time]

    if filtered_fs.shape[0] > 100_000:
        # Downsample to make plotting faster
        filtered_fs = filtered_fs.loc[::filtered_fs.shape[0]//100_000]

    for column in filtered_fs.columns:
        if '3G' in column: 
            plt_num=0
        else:
            plt_num=1
        cx[plt_num].plot(filtered_fs.index, filtered_fs[column], label=column)

    for c in cx:
        c.legend(loc=1, bbox_to_anchor=(1.1, 1.05))
        c.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(bysecond=[30]))
        c.grid(which='both', linestyle='--')

    cx[-1].xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_fn))
    cx[-1].set_xlabel("date\ntime\n"+'\n'.join(xlabel_variables))
    cx[-1].xaxis.set_label_coords(-0.07,-0.06)
    plt.subplots_adjust(bottom=0.25)

    save_name = (f'{datetime.strftime(start_time, "%Y%m%d_%H%M")}_'
                f'{datetime.strftime(end_time, "%H%M")}_BARREL_'
                '3G_3F_fast_spectra.png')
    plt.savefig(pathlib.Path('plots', time_freq, save_name), dpi=200)
    cx[0].clear()
    cx[1].clear()

plt.show()