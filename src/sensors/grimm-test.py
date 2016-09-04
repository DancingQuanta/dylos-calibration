#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from src.modules.data import *
from src.modules.calibration import *
from datetime import datetime as dt

start = dt(2016, 7, 4, 10, 30)
end = dt(2016, 7, 4, 10, 35)

print("Grimm")
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir,
                                           os.pardir))

path = os.path.join(project_dir, "data", "raw", "grimm.log")

# Fetch information about bin boundaries for this sensor
bins = ['', 0.3, 0.4, 0.5, 0.65, 0.8, 1, 1.6, 2, 3, 4, 5, 7.5, 10, 15, 20, 30]

# Load data
bins = loadData(path, bins, "grimm")

# Select data
data = bins['data'].loc[start:end]

# Resample data
data = data.resample('T',label='left', closed='left').mean()

# Grimm data is shifted 7 minutes ahead.
data.index = data.index - pd.DateOffset(minutes=7)

# New bin boundaries
bins2 = [0.5,2.5,10]

# Rebin grimm data to different bin boundaries
rebinned = rebin(bins, bins2)

mean = data.mean()
print(mean)
meandf = pd.DataFrame([mean])
print(meandf)

mean = rebinned.mean()
print(mean)
meandf = pd.DataFrame([mean])
print(meandf)

