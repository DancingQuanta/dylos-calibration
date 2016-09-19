#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Process alphasense dataset
Alphasense data is produced when Raspberry pi asks for it.

The sensor output data consisting of a histogram of 16 bins, sampling period
and sample flow rate measured each sample cycle.
The histogram produced by the sensor is a total counts of particles in each bin
for a whole sample period.
The sampling period is the length of time of counting particles.
The sampling period is normally less than the sampling period of the raspberry
pi because of the delay in communication.
The delay is about 0.1 seconds.
The sample flow rate is the rate of volumn of air through the sensor.
The sampling period must be between 1.4 and 10 seconds.

When the raspberry pi starts to sample data from the sensor, the first
datapoint have a sampling period very different from the expected sampling
period and so should be rejected.

To obtain the particle concentration, divide the total by the product of the
flow rate and sampling period.

The sample flow rate of Alphasense OPC-N2 is normally 220 ml/min.

The function of this script are:

    Removes data with wrong sampling periods

    Converts the histogram to particle concentration in 1/cm3.

    Resample the data to 1 minute frequency.

    Checks for any gaps in time and produce separate datafiles of data that do
    not have time gaps.

"""

import os
import sys
from operator import itemgetter
from itertools import groupby
import numpy as np
import pandas as pd
from pint import UnitRegistry

# Initialise pint's UnitRegistry
ureg = UnitRegistry()


def argparse(argv):
    """Parse commandline arguments.
    Expects input file path
    """
    try:
        inputfile = str(argv[1])
    except:
        error = argv[0] + " <inputfile>"
        print(error)
        sys.exit(2)
    if os.path.isfile(inputfile):
        print('Input file is', inputfile)
        return inputfile
    else:
        print("Inputfile does not exist")
        sys.exit(2)


def loadData(path):
    """Load Alphasense dataset
    """
    cols = ['Datetime', 'Bin 0', 'Bin 1', 'Bin 2', 'Bin 3',
            'Bin 4', 'Bin 5', 'Bin 6', 'Bin 7',
            'Bin 8', 'Bin 9', 'Bin 10', 'Bin 11',
            'Bin 12', 'Bin 13', 'Bin 14', 'Bin 15',
            'Bin1 MToF', 'Bin3 MToF', 'Bin5 MToF', 'Bin7 MToF',
            'Sampling Period', 'Temperature',
            'Pressure', 'PM1', 'PM2.5', 'PM10', 'SFR']
    # Load data
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col='Datetime',
                     infer_datetime_format=True,
                     header=None,
                     names=cols)

    return df


def concentration(df):
    """
    Convert total counts to concentration using sampling period and sample
    flow rate measured during samping
    """
    print("Converting histogram to concentration")

    cols = ['Bin 0', 'Bin 1', 'Bin 2', 'Bin 3',
            'Bin 4', 'Bin 5', 'Bin 6', 'Bin 7',
            'Bin 8', 'Bin 9', 'Bin 10', 'Bin 11',
            'Bin 12', 'Bin 13', 'Bin 14', 'Bin 15']

    # Compute scale
    flowratw = ureg("220 ml/min")
    sampleperiod = ureg("s")
    vol = (flowratw * sampleperiod).to("cm ** 3").magnitude
    # Now vol is just a scale number between units and that have
    # not been multipled with magnitude of sampling period yet,

    # Divide the histogram
    samplingperiod = ureg('s') * df['Sampling Period']
    flowrate = ureg('ml/s') * df['SFR']
    vol = flowrate * samplingperiod
    df['Total Volume'] = (vol).to('cm ** 3').magnitude
    df[cols] = df[cols].div(df['Total Volume'], axis=0)

    print("Successfully converted")
    return df


def findGroups(index):
    """
    Find group of consective sequence
    """

    ranges = []
    for k, g in groupby(enumerate(index), lambda ix: ix[1]-ix[0]):
        group = list(map(itemgetter(1), g))
        ranges.append((group[0], group[-1]))
    return ranges


def main(inputfile):
    print("Processing data!")
    # load data
    data = loadData(inputfile)

    # Find index of rows with period between 9 and 11 seconds.
    index = [i for i, x in enumerate(data['Sampling Period'].values)
             if not 9 < x < 11]
    # Drop rows with incorrect periods
    data = data.drop(data.index[index])

    # Calculate concentration
    data = concentration(data)

    # Resample to minute frequency
    data = data.resample('T', label='left', closed='left').mean()

    # Find segments between Nan
    date_range = pd.date_range(min(data.index), max(data.index), freq='T')
    data = data.reindex(date_range)
    ts = data[data.columns[0]]
    index = np.where(ts.notnull())[0]
    ranges = findGroups(index)

    # Generate path to split data
    name = os.path.basename(inputfile)
    name = os.path.splitext(name)[0]
    path = os.path.abspath(inputfile)
    path = os.path.dirname(path)
    path = os.path.join(path, "split-" + name)
    if not os.path.isdir(path):
        os.mkdir(path)

    # Open a file to write processed data
    path1 = os.path.join(path, name)
    fid = open(path1, "a")

    # Analyse data for time gaps (NaN)
    if len(ranges) != 0:
        start,  end = zip(* ranges)
        startdt = data.index[list(start)]
        enddt = data.index[list(end)]
        dict = {"Startx": start, "Endx": end,
                "Startdt": startdt, "Enddt": enddt}
        columns = ["Startx", "Endx", "Startdt", "Enddt"]
        df = pd.DataFrame(dict, columns=columns)
        for i in range(0, len(ranges)):
            segment = data.iloc[start[i]:(end[i]+1)]
            startdt = segment.index[0].strftime("%Y-%m-%d_%H-%M-%S")
            enddt = segment.index[-1].strftime("%Y-%m-%d_%H-%M-%S")
            filename = "%s_%s_%s" % (startdt, enddt, name)
            path2 = os.path.join(path, filename)
            segment.to_csv(path2, header=None)
            segment.to_csv(fid, header=None)
        print(df)
    else:
        print("All Nan!")
        return None
    fid.close()

if __name__ == "__main__":
    inputfile = argparse(sys.argv)
    main(inputfile)
