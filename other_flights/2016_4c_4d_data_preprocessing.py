# Script that calls the data_processing.py program and analyze the
# BARREL flight data from the 2016 flights 3G and 3F. The fast 
# spectra and ephemeris data is merged from the 3G and 3F balloons
# for every date in flight_dates and saved to ./merged_data/ folder
# (created if does not exist).

import pathlib
# import os 
# import spacepy.pycdf

import directories
import data_preprocessing

flight_dates = ['20160821', '20160822']
campaign_dir = pathlib.Path(directories.data_dir, 'campaign_4')

# Make merged_data directory if it does not exist yet.
if not pathlib.Path('merged_data').is_dir():
    pathlib.Path('merged_data').mkdir(parents=True, exist_ok=True)
    print(f'Made a merged_data/ directory')

### EPHEMERIS PROCESSING ###
ephem_match_name = 'bar_*_l2_ephm_*.cdf'
ephem_save_name = 'barrel_4c_4d_merged_ephemeris.csv'

ephem_paths = sorted(campaign_dir.rglob(ephem_match_name), 
                key=lambda i: i.name.split('_')[4])
print('2016 BARREL campaign fast ephemeris files sorted by date'
    ' (not all will be processed):')

for path in ephem_paths:
    print(path.name)

"""
For reference here are the files I have.
bar_4C_l2_ephm_20160821_v06.cdf
bar_4D_l2_ephm_20160821_v06.cdf
bar_4C_l2_ephm_20160822_v06.cdf
bar_4D_l2_ephm_20160822_v06.cdf

bar_4G_l2_ephm_20160829_v06.cdf
bar_4F_l2_ephm_20160829_v06.cdf
bar_4G_l2_ephm_20160830_v06.cdf
bar_4H_l2_ephm_20160830_v06.cdf
"""

ephem = {date:{} for date in flight_dates}

for path in ephem_paths:
    flight_date = path.name.split('_')[4]
    payload = path.name.split('_')[1]

    if flight_date in flight_dates:
        # Load the ephemeris data into ephem dictionary with date keys.
        # For each key date, save the dataframe into a payload dictionary.
        ephem[flight_date][payload] = data_preprocessing.load_barrel_ephem(str(path))

ephem_merged = {}

for date in ephem:
    ephem_merged[date] = data_preprocessing.merge_ballon_data(ephem[date])

ephem_merged = data_preprocessing.merge_ballon_times(ephem_merged)

# Calculate the balloon separation.
ephem_merged['dist_km'] = data_preprocessing.haversine(
                    ephem_merged[['4C_GPS_Lat', '4C_GPS_Lon', '4C_GPS_Alt']], 
                    ephem_merged[['4D_GPS_Lat', '4D_GPS_Lon', '4D_GPS_Alt']]
                                                        )
ephem_merged.to_csv(pathlib.Path('merged_data', ephem_save_name), 
                    index_label='Time')

# # ### FAST SPECTRA PROCESSING ###
fs_match_name = 'bar_*_l2_fspc_*.cdf'
fs_save_name = 'barrel_4c_4d_merged_fast_spectra.csv'

fs_paths = sorted(campaign_dir.rglob(fs_match_name), 
                key=lambda i: i.name.split('_')[4])

print('2016 BARREL campaign fast spectra files sorted by date'
    ' (not all will be processed):')
for path in fs_paths:
    print(path.name)

# Make a dictionary of dictionaries. The parent level dictionary
# has the dates and the child dictionary has the payloads that 
# flew on those days.
fs = {date:{} for date in flight_dates}

for path in fs_paths:
    flight_date = path.name.split('_')[4]
    payload = path.name.split('_')[1]

    if flight_date in flight_dates:
        # Load the fast spectra data into ephem dictionary with date keys.
        # For each key date, save the dataframe into a payload dictionary.
        fs[flight_date][payload] = data_preprocessing.load_barrel_spectra(str(path))

fs_merged = {}

for date in fs:
    fs_merged[date] = data_preprocessing.merge_ballon_data(
                            fs[date], 
                            tolerance_min=1/60
                            )

fs_merged = data_preprocessing.merge_ballon_times(fs_merged)

fs_merged.to_csv(pathlib.Path('merged_data', fs_save_name), 
                    index_label='Time')