#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
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


if __name__ == "__main__":
    inputfile = argparse(sys.argv)

    print("Processing data!")
    # load data
    data = loadData(inputfile)

    data.index = data.index.values.astype('<M8[m]')
    print(len(data.index))
    dups = data.index.duplicated(keep='first')
    index_dups = data.index[dups]
    print(index_dups)
