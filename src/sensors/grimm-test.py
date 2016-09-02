#!/usr/bin/env python
# -*- coding: utf-8 -*-

from grimm import *
from datetime import datetime as dt

start = dt(2016, 7, 4, 10, 30)
end = dt(2016, 7, 4, 10, 35)

print("Grimm")
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
path = os.path.join(project_dir, "data", "raw", "grimm.log")
grimmData = loadGrimmData(path).loc[start:end]
grimmData = grimmData.resample('T',label='left', closed='left').mean()
# Grimm data is shifted 7 minutes ahead.
grimmData.index = grimmData.index - pd.DateOffset(minutes=7)

mean = grimmData.mean()
meandf = pd.DataFrame([mean])
bins1 = {'columns': ['0.23-Grimm','0.3-Grimm','0.4-Grimm','0.5-Grimm','0.65-Grimm',
          '0.8-Grimm','1-Grimm','1.6-Grimm','2-Grimm','3-Grimm','4-Grimm',
          '5-Grimm','7.5-Grimm','10-Grimm','15-Grimm','20-Grimm'],
         'bounds': [0.23,0.3,0.4,0.5,0.65,0.8,1,1.6,2,3,4,5,7.5,10,15,20,30]}

bins2 = {'columns': ['0.5-Grimm', '2.5-Grimm'],
         'bounds': [0.5,2.5,30]}

data = rebin(grimmData,bins1,bins2)
print(data)
data = remapGrimm(grimmData)
print('remap')
print(data)
