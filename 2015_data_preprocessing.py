# Script that calls the data_processing.py program and analyze the
# BARREL flight data from the 2015 flights 3G and 3F. The fast 
# spectra and ephemeris data is merged from the 3G and 3F balloons
# for every date in flight_dates and saved to ./merged_data/ folder
# (created if does not exist).

import pathlib
# import os 
# import spacepy.pycdf

import directories
import data_preprocessing

flight_dates = ['20150825', '20150826']
campaign_dir = pathlib.Path(directories.top_dir, 'campaign_3')

# Make merged_data directory if it does not exist yet.
if not pathlib.Path('merged_data').is_dir():
    pathlib.Path('merged_data').mkdir(parents=True, exist_ok=True)
    print(f'Made a merged_data/ directory')

### EPHEMERIS PROCESSING ###
ephem_match_name = 'bar_*_l2_ephm_*.cdf'
flight_dates = ['20150825', '20150826'] # Flight days to plot
ephem_save_name = 'barrel_3g_3f_merged_ephemeris.csv'

ephem_paths = sorted(campaign_dir.rglob(ephem_match_name), 
                key=lambda i: i.name.split('_')[4])
print('2015 BARREL campaign fast ephemeris files (not all will be processed):')
for path in ephem_paths:
    print(path.name)

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
                    ephem_merged[['3G_GPS_Lat', '3G_GPS_Lon', '3G_GPS_Alt']], 
                    ephem_merged[['3F_GPS_Lat', '3F_GPS_Lon', '3F_GPS_Alt']]
                                                        )
ephem_merged.to_csv(pathlib.Path('merged_data', ephem_save_name), 
                    index_label='Time')

# ### FAST SPECTRA PROCESSING ###
fs_match_name = 'bar_*_l2_fspc_*.cdf'
fs_save_name = 'barrel_3g_3f_merged_fast_spectra.csv'

fs_paths = sorted(campaign_dir.rglob(fs_match_name), 
                key=lambda i: i.name.split('_')[4])

print('2015 BARREL campaign fast spectra files (not all will be processed):')
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
    fs_merged[date] = data_preprocessing.merge_ballon_data(fs[date])

fs_merged = data_preprocessing.merge_ballon_times(fs_merged)

fs_merged.to_csv(pathlib.Path('merged_data', fs_save_name), 
                    index_label='Time')