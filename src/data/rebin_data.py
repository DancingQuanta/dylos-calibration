#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import json
import numpy as np
import pandas as pd
from rebin import *
from utils import *


def load_data(path):
    """Load a dataset
    """
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col=0,
                     infer_datetime_format=True)
    return df


def rebin(df, bins1, bins2):
    """Rebin binned data to new bin boundaries.
    Uses the rebin_piecewise_constant function from jhykes/rebin github repo.

    Args:
        df: Pandas: DataFrame
        bins1 : list of float
            List of low bin boundary positions, with the
            last element being the top boundary of last bin.
        bins2 : list of float
            The list is the low bin boundary positions, with the
            last element being the top boundary of last bin.
            This list will be used to rebin the 'data' in bins1
    Return:
        df: Pandas.DataFrame
            Output DataFrame with newly changed bins boundaries
    """

    # Get column labels
    columns1 = df.columns
    # What sensor it is
    sensorName = columns1[0].split('-')[0]
    # Old bins
    bounds1 = bins1

    # Generate new bins labels
    bins2 = gen_bin_labels(bins2, sensorName)
    bounds2 = bins2['bounds']
    columns2 = bins2['columns']

    # Ensure the lower boundary of lowest bin and upper boundary of
    # highest bin of new bin list is within the limits of old bin list
    if bounds2[0] < bounds1[0]:
        msg = ("The lower boundary of new bottommost bin (%s)"
               "is lower then the lower boundary of old mottommost"
               "bin (%s)" % (bounds2[0], bounds1[0]))
        raise ValueError(msg)
    if bounds2[-1] > bounds1[-1]:
        msg = ("The upper boundary of new topmost bin (%s)"
               "is higher then the upper boundary of old topmost"
               "bin (%s)" % (bounds2[-1], bounds1[-1]))
        raise ValueError(msg)

    # Assign bin boundaries
    x1 = np.array(bounds1)
    x2 = np.array(bounds2)

    # Check if input data is a series or dataframe
    if isinstance(df, pd.Series):
        y1 = df.values
        y2 = rebin_piecewise_constant(x1, y1, x2)
        # Initialise new dataframe
        df2 = pd.Series(y2, index=columns2)
    elif isinstance(df, pd.DataFrame):
        index = df.index
        # Initialise new dataframe
        df2 = pd.DataFrame(0, index=index, columns=columns2)
        for ix in index:
            y1 = df.loc[ix].values
            y2 = rebin_piecewise_constant(x1, y1, x2)
            df2.loc[ix] = y2

    return df2


if __name__ == '__main__':
    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Settings yaml file")

    options = parser.parse_args()
    settings_file = options.settings    # Settings file

    # Load settings json file
    with open(settings_file) as handle:
        settings = json.load(handle)

    # Load info
    calibrater = settings['calibration']['calibrater']
    calibratee = settings['calibration']['calibratee']
    sensors = settings['sensors']

    # Get bin boundaries
    calibrater_bins = sensors[calibrater]['bins']
    calibratee_bins = sensors[calibratee]['bins']

    # Name of rebinned dataset
    name = "rebinned-" + calibrater

    # Append to sensor order
    if name not in settings['sensor_order']:
        settings['sensor_order'] += [name]

    # Append to calibration
    if 'rebinned' not in settings['calibration']:
        settings['calibration']['rebinned'] = name

    # Give details of rebinned dataset
    sensors[name] = {}
    sensors[name]['bins'] = calibratee_bins
    sensors[name]['name'] = "Rebinned\n%s" % (sensors[calibrater]['name'])

    settings['sensors'] = sensors

    # Conditions
    order = settings['exp']['order']
    conditions = settings['exp']['conditions']

    for exp in order:
        condition = conditions[exp]

        # Load data path
        calibrater_path = condition['sensor'][calibrater]['data']

        # Load data
        calibrater_data = load_data(calibrater_path)

        # rebin calibrater dataset to match calibratee dataset
        rebinned = rebin(calibrater_data, calibrater_bins, calibratee_bins)
        dir = os.path.dirname(calibrater_path)
        path = writeData(rebinned, dir, name)
        condition['sensor'][name] = {'data': path}
        conditions[exp] = condition

    settings['exp']['conditions'] = conditions

    # Output processed data
    with open(settings_file, 'w') as handle:
        json.dump(settings, handle, default=date_handler,
                  sort_keys=True, indent=4)


