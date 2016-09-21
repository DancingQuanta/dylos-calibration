#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from datetime import datetime, timedelta
import logging
import json
import pandas as pd
from pint import UnitRegistry
import yaml
from collections import defaultdict
from utils import gen_bin_labels


def date_handler(obj):
    # Handles datetime object before json serialising it
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    # else:
        # raise TypeError


def load_data(path, bins, string):
    """Load binned data into a Pandas.DataFrame where first column is datetime,
    each columns represent a bin and name each column according to a list of
    floats in argument.

    Args:
        path : string
            path to datafile
        bins : list
        List of floats of bin boundaries, where every except the last element
        represent lower bin boundary and the last is uppper bin boundary of the
        last bin.
    Returns:
        df: Pandas.DataFrame

    """
    # Use list of bin boundaries to generate a list of bin labels for the
    # DataFrame
    bins = gen_bin_labels(bins, string)

    # Set the labels of DataFrame columns
    # Generate indexes of elements in columns to load, if any element is an
    # empty string do not include its index.
    cols = ['DateTime'] + bins['columns']
    usecols = [0] + [x + 1 for x in bins['index']]

    # Load data
    df = pd.read_csv(path,
                     parse_dates={"Datetime": [0]},
                     index_col='Datetime',
                     infer_datetime_format=True,
                     header=None,
                     names=cols,
                     usecols=usecols)

    # Return the data
    return df, bins['bounds']


def writeData(df, path, filename):
    """Write Pandas.DataFrame to csv file
    Args:
        df: Pandas.DataFrame
        path: string
            Path to location of file
        filename: str
            Name of the file
    Returns: None
    """
    filename = filename + ".csv"
    path = os.path.join(path, filename)
    df.to_csv(path)
    return path


def realCounts(data):
    """Subtract the upper bins from the lower bins
    """
    # Get number of columns, loop over, sum upper and subtract from lower.
    columns = data.columns
    for i in range(0, len(columns)):
        sumup = data[columns[(i+1):]].sum(axis=1)
        data[columns[i]] = data[columns[i]] - sumup
    return data


def pruneBins(df):
    """Drop bins if they have zero counts in the mean.

    Args:
        data : Pandas.DataFrame
    Returns:
        data; Pandas.DataFrame
            The dataframe will have fewer columns.
    """
    # Initialise new dataframe
    df1 = pd.DataFrame(columns=['Counts'])
    df1['Counts'] = df.mean(axis=0)

    # Loop over columns
    for ix, key in enumerate(df1.index):
        counts = np.round(df1['Counts'].iloc[ix])
        # Do not want to display histogram of bins at large sizes if
        # the counts is zero.
        if counts == 0:
            zeroColumns = zeroColumns + [ix]
        elif counts > 0:
            zeroColumns = []

    # Drop columns using zeroColumns
    df = df.drop(df.columns[zeroColumns], axis=1)
    return df


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
    sensorsFile = options.sensors      # Sensor configuration file
    raw_data_dir = options.rawdatadir  # Root directory of raw data
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

    # Final particle concentration
    outputUnit = ureg(settings['output']['unit'])

    # Sensors
    sensors = settings['sensors']

    # Experimental conditions
    exps = settings['exp']

    # Conditions
    order = exps['order']
    conditions = exps['conditions']
    # Add keys to conditions
    for a in list(conditions):
        conditions[a]['sensor'] = {}

    # Load sensors definitions
    with open(sensorsFile) as handle:
        sensorDefinition = yaml.load(handle)

    debug = ("Loading sensor data")
    logging.debug(debug)

    # Load data for a sensor
    for sensor in sensors:
        logging.debug("Sensor: %s" % (sensor))
        # Load config for a sensor
        config = sensors[sensor]

        # What type of sensor it is?
        type = config['type']

        # Load sensor definition
        config.update(sensorDefinition[type])

        # Where is the data in data/raw/?
        sensor_dir = config['path']
        data_dir = os.path.join(raw_data_dir, sensor_dir)

        # Fetch information about bin boundaries for this sensor
        bins = config['bins']

        # Load data
        data, bins = load_data(data_dir, bins, sensor)

        # Update bins
        config['bins'] = bins

        # If the data is not in minute frequency, resample it
        if 'resample' in config:
            if 'minute' == config['resample']:
                data = data.resample('T', label='left', closed='left').mean()

        if 'realcounts' in config:
            # Subtract high bins from lower
            data = realCounts(data)

        # How much time should the data produced by this sensor be shifted?
        # Shift datetime index of data
        if 'timeshift' in config:
            timeshift = config['timeshift']
            sign = timeshift[0]
            period = timeshift[1:]
            t = datetime.strptime(period, "%H:%M:%S")
            delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            debug = "Time shifted by %s %s" % (sign, str(delta))
            logging.debug(debug)
            debug = ("Before timeshift\n"
                     "Start: %s, end: %s" % (data.index[0], data.index[-1]))
            logging.debug(debug)
            if sign == '-':
                data.index = data.index - delta
            elif sign == '+':
                data.index = data.index + delta
            else:
                raise ValueError("Sign not given for timeshift")
            debug = ("After timeshift\n"
                     "Start: %s, end: %s" % (data.index[0], data.index[-1]))
            logging.debug(debug)

        # Set seconds to zero
        data.index = data.index.values.astype('<M8[m]')

        # Units of data
        # Scaling and unit conversion of particle concentration
        # What is the unit of recorded measurements?
        inputUnit = ureg(config['unit'])
        if "flowrate" in config:
            inputFlowrate = ureg(config['flowrate'])

        # Create test quantities to compare dimensionality against
        counts_test = ureg("counts")
        vol_test = ureg("m ** 3")
        conc_test = counts_test / vol_test
        time_test = ureg("s")
        rate_test = counts_test / time_test
        flowrate_test = vol_test * rate_test

        # Compare dimensionality of input data and output unit
        # If output unit is concentration
        if outputUnit.dimensionality == conc_test.dimensionality:

            # If input unit is concentration
            if inputUnit.dimensionality == conc_test.dimensionality:
                scale = inputUnit.to(outputUnit).magnitude
                # scale = 1/float(outputUnit / inputUnit)
                if 'concentration' not in config:
                    config['concentration'] = str('{:.03f~}'.format(inputUnit))
                # Calculate count rate if not exists
                if 'count rate' not in config:
                    countrate = (inputFlowrate * inputUnit).to('counts/s')
                    config['count rate'] = str('{:.03f~}'.format(countrate))

            # If input unit is count rate
            elif inputUnit.dimensionality == rate_test.dimensionality:
                conc = inputUnit / inputFlowrate
                scale = float(outputUnit / conc)
                if 'count rate' not in config:
                    config['count rate'] = str('{:.03f}'.format(inputUnit))
                if 'concentration' not in config:
                    config['concentration'] = str('{:.03f}'.format(conc))

            else:
                msg = "The input unit is incorrect or not yet implementated!"
                raise ValueError(msg)
        else:
            msg = "The output unit is incorrect or not yet implementated!"
            raise ValueError(msg)

        config['scale factor'] = scale
        debug = "The scaling factor is %s" % (scale)
        logging.debug(debug)

        # Update sensor dict with settings
        sensors[sensor] = config

        # Multiply the data with scale factor
        data = data*scale

        # Save processed data
        full_path = os.path.join(output_dir, 'full')
        if not os.path.isdir(full_path):
            os.makedirs(full_path)
        path = writeData(data, full_path, sensor)

        conditions['full'] = {}
        conditions['full']['sensor'] = {}
        conditions['full']['sensor'][sensor] = {}
        conditions['full']['sensor'][sensor]['data'] = path

        # Loop over different conditions and save part of data relevant to that
        # period

        logging.debug("Experiment time")
        # Iterate over different experiment conditions
        for exp in order:
            # Make condition path if not exist
            path = os.path.join(output_dir, exp)
            if not os.path.isdir(path):
                os.makedirs(path)

            condition = conditions[exp]

            # Load start and end datetime for time series data
            start = condition['start']
            end = condition['end']

            # Select data
            sample = data.loc[start:end].copy(deep=True)

            # Check if any bins have zero counts and drop them
            if 'prunebins' in sensors:
                # Prune bins from data that have zero counts
                sample = pruneBins(sample)

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
