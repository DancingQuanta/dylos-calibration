#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd


def rebinAlpha(data):
    """Rebin Alphasense OPC-N2 dataset to new bin boundaries;
    >0.5um and >2.5um up to  10um.
    """

    bottombin = ['alpha-0.38']
    bottomhalf = ['alpha-0.38', 'alpha-0.54', 'alpha-0.78', 'alpha-1.05',
                  'alpha-1.34', 'alpha-1.59']
    middlebin = ['alpha-2.07']
    tophalf = ['alpha-3.0', 'alpha-4.0', 'alpha-5.0', 'alpha-6.5', 'alpha-8.0']

    # Check if input data is a series or dataframe
    if isinstance(data, pd.Series):
        data.loc[bottombin] *= (0.04)/(0.16)
        bottom_middle = data.loc[middlebin] * (2.5-2.07)/(3.0-2.07)
        top_middle = data.loc[middlebin] * (3.0-2.5)/(3.0-2.07)
        bottom = data.loc[bottomhalf].sum()
        top = data.loc[tophalf].sum()
        index = [0]
    elif isinstance(data, pd.DataFrame):
        index = data.index
        print(data)
        data[bottombin] *= (0.04)/(0.16)
        bottom_middle = data[middlebin] * (2.5-2.07)/(3.0-2.07)
        top_middle = data[middlebin] * (3.0-2.5)/(3.0-2.07)
        bottom = data[bottomhalf].sum(axis=1)
        top = data[tophalf].sum(axis=1)
        print("bottom")
        print(bottom)
        print(top)

    columns = ['0.5-alpha', '2.5-alpha']
    rebinned = pd.DataFrame(index=index, columns=columns)

    rebinned['0.5-alpha'] = bottom.values + bottom_middle.values
    rebinned['2.5-alpha'] = top.values + top_middle.values

    return rebinned
