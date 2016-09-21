#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import logging
import json
import pandas as pd
from pint import UnitRegistry
import yaml
from utils import gen_bin_labels


def load_data(path):
    """Load a dataset
    """
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col='Datetime',
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
            Output DataFrame with newly changed bins bounbaries
    """

    # Get column labels
    columns1 = df.columns
    # What sensor it is
    sensorName = columns1[0].split('-')[0]


    bins2 = generateBinLabels(bins2, label)

    # Ensure the lower boundary of lowest bin and upper boundary of
    # highest bin of new bin list is within the limits of old bin list
    if bins2['bounds'][0] < bins1['bounds'][0]:
        msg = ("The lower boundary of new bottommost bin (%s)"
               "is lower then the lower boundary of old mottommost"
               "bin (%s)" % (bins2['bounds'][0], bins1['bounds'][0]))
        raise ValueError(msg)
    if bins2['bounds'][-1] > bins1['bounds'][-1]:
        msg = ("The upper boundary of new topmost bin (%s)"
               "is higher then the upper boundary of old topmost"
               "bin (%s)" % (bins2['bounds'][-1], bins1['bounds'][-1]))
        raise ValueError(msg)

    # Assign bin boundaries
    x1 = np.array(bins1['bounds'])

if __name__ == '__main__':
    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Settings yaml file")
    parser.add_argument("sensors", help="Sensors defintions yaml file")
    parser.add_argument("rawdatadir", help="Raw Data directory")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")

    options = parser.parse_args()
    settingsFile = options.settings    # Settings file
    outputFile = options.output        # Output directory

    name = os.path.basename(settingsFile)
    name = os.path.splitext(name)[0]

    # Create output directory
    filename = os.path.basename(outputFile)
    name = os.path.splitext(filename)[0]
    path = os.path.abspath(os.path.dirname(outputFile))
    output_dir = os.path.join(path, name)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Initialise pint's UnitRegistry
    ureg = UnitRegistry()

    # Load settings yaml file
    with open(settingsFile) as handle:
        settings = yaml.load(handle)

    # Load info
    calibration = settings['calibration']
    sensors = settings['sensors']
    exps = setttings['exp']

    # Conditions
    order = exps['order']
    conditions = exps['conditions']

    # Get sensor details
    calibrater = sensors[calibration['calibrater']]
    calibratee = sensors[calibration['calibratee']]

    for exp in order:
        condition = conditions[exp]

        # Load data path
        calibrater_path = condition['sensor'][calibration['calibrater']]
        calibratee_path = condition['sensor'][calibration['calibratee']]

        # Load data
        calibrater_data = load_data(calibrater_path)
        calibratee_data = load_data(calibratee_path)

        # Get bin boundaries
        calibrater_bins = cablirater['bins']
        calibratee_bins = cabliratee['bins']



        # Bin boundaries of final set of bins
        finalBins = calibratee['bounds']

        # rebin calibrater dataset to match calibratee dataset
        rebinned = rebin(calibrater, finalBins)
        name = "rebinned-" + sensors['calibrater']['id']
        writeData(rebinned['data'], base_interim_data_dir, name)
        debug = ("Start: %s, end: %s" % (rebinned['data'].index[0],
                                         rebinned['data'].index[-1]))
        logging.debug(debug)
        sensors['rebinned'] = {'id': name, 'bins': rebinned}


        # Write selected data to file
        path = writeData(sample, path, sensor)

        condition['sensor'][sensor] = {'data': path}

        conditions[exp] = condition

    exps['conditions'] = conditions


    # Output processed data
    dump = json.dumps(settings, default=date_handler,
                      sort_keys=True, indent=4).replace("\\\\", "/")
    with open(outputFile, 'w') as outfile:
            outfile.write(dump)
