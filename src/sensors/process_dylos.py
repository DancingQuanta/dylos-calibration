#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Process dylos dataset
"""
import os
import sys
from operator import itemgetter
from itertools import groupby
import numpy as np
import pandas as pd

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
    cols = ['Datetime', "Bin 0", "Bin 1"]
    # Load data
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col='Datetime',
                     infer_datetime_format=True,
                     header=None,
                     names=cols)

    df.index = df.index.values.astype('<M8[m]')
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

    data.index = data.index.values.astype('<M8[m]')

    ts = data[data.columns[0]]
    # Fill missing data with NaNs
    ts = ts.reindex(pd.date_range(min(ts.index), max(ts.index), freq='T'))

    index = np.where(ts.notnull())[0]

    ranges = findGroups(index)
    if len(ranges) != 0:
        start,  end = zip(* ranges)
        # startdt = data.index[list(start)]
        # enddt = data.index[list(end)]
        # dict = {"Startx": start, "Endx": end,
                # "Startdt": startdt, "Enddt": enddt}
        # columns = ["Startx", "Endx", "Startdt", "Enddt"]
        # df = pd.DataFrame(dict, columns=columns)
        for i in range(0, len(ranges)):
            segment = data.iloc[start[i]:(end[i]+1)]
            startdt = segment.index[0].strftime("%Y-%m-%d_%H-%M-%S")
            enddt = segment.index[-1].strftime("%Y-%m-%d_%H-%M-%S")
            filename = "%s_%s_%s" % (startdt, enddt, name)
            path2 = os.path.join(path, filename)
            segment.to_csv(path2, header=None)
            segment.to_csv(fid, header=None)
        # return df
    else:
        print("All Nan!")
        return None
    fid.close()


if __name__ == "__main__":
    inputfile = argparse(sys.argv)
    main(inputfile)
