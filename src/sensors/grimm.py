#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Helper functions for Grimm Aerosol spectrometer

import pandas as pd

def averageSize(df):
    df['AverageGrimm'] = (df['0.23-Grimm']*0.23+df['0.3-Grimm']*0.3+df['0.4-Grimm']*0.4+df['0.5-Grimm']*0.5+
                   df['0.65-Grimm']*0.65+df['0.8-Grimm']*0.8+df['1-Grimm']*1+df['1.6-Grimm']*1.6+
                   df['2-Grimm']*2+df['3-Grimm']*3+df['4-Grimm']*4+df['5-Grimm']*5+
                   df['7.5-Grimm']*7.5+df['10-Grimm']*10+df['15-Grimm']*15+df['20-Grimm']*20
                  )/(df['0.23-Grimm']+df['0.3-Grimm']+df['0.4-Grimm']+df['0.5-Grimm']+
                     df['0.65-Grimm']+df['0.8-Grimm']+df['1-Grimm']+df['1.6-Grimm']+
                     df['2-Grimm']+df['3-Grimm']+df['4-Grimm']+df['5-Grimm']+
                     df['7.5-Grimm']+df['10-Grimm']+df['15-Grimm']+df['20-Grimm'])
    return df

def rebinGrimm(data):
    """Rebin grimm 1.108 dataset to new bin boundaries, >0.5um and >2.5um up to
    10um.
    """
    bottomhalf = ['grimm-0.5', 'grimm-0.65', 'grimm-0.8',
                  'grimm-1', 'grimm-1.6', 'grimm-2']
    middlehalf = ['grimm-2']
    tophalf = ['grimm-2', 'grimm-3', 'grimm-4',
               'grimm-5', 'grimm-7.5']

    # Check if input data is a series or dataframe
    if isinstance(data, pd.Series):
        data.loc[middlehalf] /= 2
        # middle = data.loc[middlehalf].values/2
        bottom = data.loc[bottomhalf].sum()
        top = data.loc[tophalf].sum()
        index = [0]
    elif isinstance(data, pd.DataFrame):
        index = data.index
        print(data)
        data[middlehalf] /= 2
        bottom = data[bottomhalf].sum(axis=1)
        top = data[tophalf].sum(axis=1)
        print("bottom")
        print(bottom)
        print(top)

    columns = ['0.5-grimm', '2.5-grimm']
    rebinned = pd.DataFrame(index=index, columns=columns)

    rebinned['0.5-grimm'] = bottom
    rebinned['2.5-grimm'] = top

    return rebinned

