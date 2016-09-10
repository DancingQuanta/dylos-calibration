#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from rebin import *
from src.modules.data import *
from src.modules.analysis import *
from grimm import rebinGrimm
from datetime import datetime as dt
from copy import deepcopy

start = dt(2016, 7, 4, 10, 30)
end = dt(2016, 7, 4, 10, 35)

print("grimm")
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir,
                                           os.pardir))

path = os.path.join(project_dir, "data", "raw", "dylos-grimm", "grimm.log")

# Fetch information about bin boundaries for this sensor
bins = ['', '', '', 0.5, 0.65, 0.8, 1, 1.6, 2, 3, 4, 5, 7.5, 10, '', '', '']

# Load data
bins = loadData(path, bins, "grimm")

# Select data
data = bins['data'].loc[start:end]

# Resample data
data = data.resample('T',label='left', closed='left').mean()

# grimm data is shifted 7 minutes ahead.
data.index = data.index - pd.DateOffset(minutes=7)

del bins['data']
bins['data'] = data

# Print original data

print("Original Data")
# print(data)

print("Mean of original data")
meanOrig = data.mean()
bins['mean'] = meanOrig
print(meanOrig)
print("Sum of mean of original data")
print(meanOrig.sum())

# print("Statistics of original data")
# midpoints = np.diff(bins['bounds'])/2 + bins['bounds'][:-1]
# print(statistics(midpoints, meanOrig.values))
# plotPath = plot(data, '.', "grimm")

# Rebin

bins2 = [0.5,2.5,10]

# Manual rebinning

print("Manual rebinning")
bins1 = deepcopy(bins)
print("Input data")
print(bins1['data'])
rebinned = rebinGrimm(bins1['data'])
print("Output data")
print(rebinned)
print(rebinned.sum())

# Rebin
del bins1
print("Rebin algorithm")
bins1 = deepcopy(bins)
print("Input data")
print(bins1['data'])
rebinned = rebin(bins1, bins2)
print("Output")
print(rebinned['data'])
print(rebinned['data'].sum())

