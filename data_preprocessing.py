import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import pathlib
import datetime

import spacepy.pycdf

"""
The two balloons in question are:
bar_3G_l2_ephm_20150825_v05.cdf
bar_3F_l2_ephm_20150825_v05.cdf
bar_3G_l2_ephm_20150826_v05.cdf
bar_3F_l2_ephm_20150826_v05.cdf
"""

Re_km = 6371

def load_barrel_ephem(path, columns='default'):
    """
    Loads the BARREL ephemeris and saves it to a pandas DataFrame.
    """
    if columns == 'default':
        columns=['GPS_Alt', 'GPS_Lat', 'GPS_Lon', 'L_Kp2', 
                'L_Kp6', 'MLT_Kp2_T89c', 'MLT_Kp6_T89c']

    ephem = spacepy.pycdf.CDF(path)
    ephem_df = pd.DataFrame({key:ephem[key][...] for key in columns}, )
    ephem_df.replace(-1E31, np.nan, inplace=True)
    ephem_df.index = ephem['Epoch'][...] 
    ephem_df.dropna(inplace=True)
    return ephem_df

def load_barrel_spectra(path):
    """
    Wrapper to load the BARREL spectra file.
    """
    columns=['FSPC1a', 'FSPC1b', 'FSPC1c', 
            'FSPC2', 'FSPC3', 'FSPC4']

    spec = load_barrel_ephem(path, columns=columns)
    # The BARREL data has time stamps out of place so the sorting 
    # patches up the problem. I understand that this may be a bad
    # thing to do.
    spec.sort_index(inplace=True)
    return spec

def merge_ballon_data(ephem, tolerance_min=5):
    """
    Merge the balloons DataFrames by time. Ephem is a dictionary 
    of DataFrames. Will merge the DataFrames with the nearest time 
    stamps. If no data point is found within tolerance_min minutes, 
    that merge will fail.
    """
    assert len(ephem.keys()) == 2, (f'Can only merge 2 DataFrames. '
                                    f'Got {len(ephem.keys())}')

    # Prefix the payload id to each the dataFrame keys.
    for payload in ephem:
        # ephem[payload].columns = ['_'.join([payload, column.split('_')[-1]]) 
        #                         for column in ephem[payload].columns]
        ephem[payload].columns = [f'{payload}_{column}' 
                                    for column in ephem[payload].columns]

    # Merge the two DataFrames 
    payload_id = [key for key, _ in ephem.items()]
    merged_df = pd.merge_asof(ephem[payload_id[0]], ephem[payload_id[1]], 
                                left_index=True, right_index=True, 
                                direction='nearest', 
                                tolerance=pd.Timedelta(minutes=tolerance_min))
    return merged_df

def merge_ballon_times(ephem):
    """
    Concatenate the ephemeris over multiple days.
    """
    return pd.concat([df for _, df in ephem.items()])

def haversine(X1, X2):
    """
    Implementation of the haversine foruma to calculate total distance
    at an average altitude. X1 and X2 must be N*3 array of 
    lat, lon, alt.
    """
    X1 = np.asarray(X1)
    X2 = np.asarray(X2)
    R = (Re_km+(X1[:, 2]+X2[:, 2])/2)
    s = 2*np.arcsin( np.sqrt( np.sin(np.deg2rad(X1[:, 0]-X2[:, 0])/2)**2 + \
                    np.cos(np.deg2rad(X1[:, 0]))*np.cos(np.deg2rad(X2[:, 0]))*\
                    np.sin(np.deg2rad(X1[:, 1]-X2[:, 1])/2)**2 ))
    return Re_km*s


if __name__ == '__main__':
    ### EXAMPLE CODE ###
    data_dir = '/home/mike/research/barrel/data/campaign_3'
    match_name = 'bar_*_l2_fspc_*.cdf'

    flight_dates = ['20150825', '20150826']

    paths = sorted(pathlib.Path(data_dir).rglob(match_name), 
                    key=lambda i: i.name.split('_')[4])

    # Make a dictionary of dictionaries. The parent level dictionary
    # has the dates and the child dictionary has the payloads that 
    # flew on those days.
    fs = {date:{} for date in flight_dates}

    for path in paths:
        flight_date = path.name.split('_')[4]
        payload = path.name.split('_')[1]

        if flight_date in flight_dates:
            # Load the fast spectra data into ephem dictionary with date keys.
            # For each key date, save the dataframe into a payload dictionary.
            fs[flight_date][payload] = load_barrel_spectra(str(path))

    merged_fs = {}

    for date in fs:
        merged_fs[date] = merge_ballon_data(fs[date])

    merged_fs = merge_ballon_times(merged_fs)
    
    
    path = ('/home/mike/research/barrel/data/campaign_3/3G/150825/'
            'bar_3G_l2_ephm_20150825_v05.cdf')
    df, time = load_barrel_ephem(path)
