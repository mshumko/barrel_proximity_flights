import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import typing

import directories
import mission_tools.misc.locate_consecutive_numbers as locate_consecutive_numbers

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

path_type = typing.NewType('path_type', pathlib.Path)

class Detect:
    def __init__(self, fs_path:path_type, ephem_path:path_type, config:typing.Dict) -> None:
        """
        Detect microbursts using the number of standard deviations 
        above the baseline method assuming Poisson statistics and
        correlate the fast spectra data between the two payloads
        """
        self.config = config
        self.fs_cadence_s = 50E-3
        self.fs_path = fs_path
        self.ephem_path = ephem_path
        return

    def load_merged_data(self) -> None:
        """
        Make sure to run data_preprocessing.py to generate the merged
        ephemeris and fast spectra data that this method loads.
        """
        self.fs = pd.read_csv(self.fs_path, parse_dates=True, index_col=0)
        self.ephem = pd.read_csv(self.ephem_path, parse_dates=True, index_col=0)

        # Filter the fast spectra and ephemeris if the time_range key is in config
        if self.config.get('time_range') is not None:
            start = self.config['time_range'][0]
            end = self.config['time_range'][1]
            self.fs = self.fs.loc[start:end]
            self.ephem = self.ephem.loc[start:end]
        return

    def rolling_correlation(self) -> None:
        """
        Use df.rolling.corr to apply a rolling cross-correlation to the
        spatially-aligned time series.
        """
        detect_channels = [column for column in self.fs.columns 
                                if self.config['detect_channel'] in column ]
        assert len(detect_channels) == 2, ('Two energy channels to '
            f'correlate not found.\n {self.config["detect_channel"]=}, '
            f'{self.fs.columns=}'
        )
        window_data_points = int(self.config['correlation_width_s']//self.fs_cadence_s)

        self.rolling_fs = self.fs[detect_channels[0]].rolling(
            window= window_data_points
            )

        self.corr = self.rolling_fs.corr(self.fs[detect_channels[1]])
        # Mark bad correlations with np.nan
        # self.corr[self.corr > 1] = np.nan
        # Now roll the self.corr to center the non-NaN values
        # self.corr = np.roll(self.corr, -window//2)
        return

    def baseline_significance(self) -> None:
        """
        Calculates the number of standard deviations, assuming Poisson statistics, that a
        a count value is above a rolling average baseline of length baseline_window.
        """ 
        detect_channels = [column for column in self.fs.columns 
                                if self.config['detect_channel'] in column ]
        assert len(detect_channels) == 2, ('Two energy channels to '
            f'correlate not found.\n {self.config["detect_channel"]=}, '
            f'{self.fs.columns=}'
        )
        baseline_window_points = int(self.config['baseline_width_min']/self.fs_cadence_s)
        rolling_average_a = self.fs[detect_channels[0]].rolling(window=baseline_window_points).mean()
        rolling_average_b = self.fs[detect_channels[1]].rolling(window=baseline_window_points).mean()
        n_std_a = (self.fs[detect_channels[0]]-rolling_average_a)/np.sqrt(rolling_average_a+1)
        n_std_b = (self.fs[detect_channels[1]]-rolling_average_b)/np.sqrt(rolling_average_b+1)
        self.n_std = pd.DataFrame(np.array([n_std_a, n_std_b]).T, columns=detect_channels)
        return

    def detect(self):
        """
        Loads the data and runs the rolling_correlation and baseline_significance methods.
        """
        self.load_merged_data()
        self.rolling_correlation()
        self.baseline_significance()
        return

    def plot_detections(self):
        """ 
        This method plots the microburst detections
        """
        fig, ax = plt.subplots(3, 1, sharex=True)
        bx = (len(ax)-1)*[None]
        # Plot the Fast Spectra data
        detect_channels = [column for column in self.fs.columns 
                                if self.config['detect_channel'] in column ]
        ax[0].plot(self.fs.index, self.fs[detect_channels[0]], 
                c='k', label=detect_channels[0])
        ax[1].plot(self.fs.index, self.fs[detect_channels[1]], 
                c='k', label=detect_channels[1])
        # Plot the correlation
        ax[2].plot(self.fs.index, self.corr, c='k')

        # Plot the baseline std values on the right-axis
        bx[0] = ax[0].twinx()
        bx[1] = ax[1].twinx()

        bx[0].plot(self.fs.index, self.n_std[d.n_std.columns[0]], c='b')
        bx[1].plot(self.fs.index, self.n_std[d.n_std.columns[1]], c='b')
        
        ax[0].set(title='BARREL microburst detection validation', ylabel=detect_channels[0])
        ax[1].set(ylabel=detect_channels[1])
        ax[2].set(ylabel='correlation', xlabel='UTC')

        bx[0].set_ylabel('Baseline n_std', color='b')
        bx[1].set_ylabel('Baseline n_std', color='b')
        bx[0].tick_params(axis='y', labelcolor='b')
        bx[1].tick_params(axis='y', labelcolor='b')
        return

if __name__ == '__main__':
    config = {
        'baseline_width_min':5,
        'baseline_std_thresh':2,
        'correlation_width_s':1,
        'correlation_thresh':0.8,
        'detect_channel':'FSPC1a',
        'time_range':['20150826T04:30:00', '20150826T08:25:00']
        }
    fs_path = pathlib.Path(directories.top_dir, 
        'merged_data', 
        'barrel_3g_3f_merged_fast_spectra.csv'
        )
    ephem_path = pathlib.Path(directories.top_dir, 
        'merged_data', 
        'barrel_3g_3f_merged_ephemeris.csv'
        )
    d = Detect(fs_path, ephem_path, config)
    d.detect()
    d.plot_detections()
    plt.show()