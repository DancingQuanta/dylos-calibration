#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Process alphasense dataset
Alphasense data is produced when Raspberry pi asks for it.

The sensor output data with a Sampling Period value which is the length of time
between sampling.
The sampleing period is normally less than the sampling period of the raspberry
pi because of the delay in communication.
The delay is about 0.1 seconds.
When the raspberry pi starts to sample data from the sensor, the first
datapoint have a sampling period less than the expected sampling period and so
can be rejected.

The histogram produced by the sensor is a total counts of particles in each bin
for a whole sample, between sampling.
To obtain the particle concentration, divide the total by the product of the
flow rate and sampling period.

The sample flow rate of Alphasense OPC-N2 is 220 ml/min.

This scripts removes data with wrong sampling periods and convert the histogram
to particle concentration in 1/cm3.
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
            'Pressure', 'PM1', 'PM2.5', 'PM10']
    # Load data
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col='Datetime',
                     infer_datetime_format=True,
                     header=None,
                     names=cols)

    return df


def concentration(df):
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
    df['Total Volume'] = df['Sampling Period'] * vol
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
    """
    Group data separated by rows with period between 59 and 65 seconds.
    """
    print("Processing data!")
    # load data
    data = loadData(inputfile)

    # Calculate concentration
    data = concentration(data)

    # Generate path to split data
    name = os.path.basename(inputfile)
    name = os.path.splitext(name)[0]

    path = os.path.abspath(inputfile)
    path = os.path.dirname(path)
    path = os.path.join(path, "split-" + name)
    if not os.path.isdir(path):
        os.mkdir(path)
    path1 = os.path.join(path, name)
    fid = open(path1,"a")

    # Find index of rows with period between 59 and 65 seconds.
    period = data['Sampling Period']
    # index = data[59 < data['Sampling Period'] < 65].index.tolist()
    # index = np.where(59 < period < 65)[0]

    index = [i for i, x in enumerate(period) if 59 < x < 65]

    ranges = findGroups(index)
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
        return df
    else:
        print("All Nan!")
        return None
    fid.close()


if __name__ == "__main__":
    inputfile = argparse(sys.argv)
    main(inputfile)
