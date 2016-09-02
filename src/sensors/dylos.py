#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.modules.tools import *

# Helper functions for Dylos aerosol sensor

def loadDylosData(path, columns=['0.5-Dylos', '2.5-Dylos']):
    df = loadData(path, columns)
    # df.index = df.index.values.astype('<M8[m]')
    return df

def plotDylos(path):
    dylosData = loadDylosData(path)
    plot(dylosData, path)

def processOriginalDylos(path):
    """
    Process the data within Dylos DC1700 and tries to match up the datetime
    with data already collected by raspberry pi.
    And then print the data out again in hourly chunks.

    """
    # Load data
    df = loadDylosData(path)
    filename = os.path.splitext(filename)[0]
    # Shift index
    df.index = df.index - pd.DateOffset(hours=1, minutes=1)
    # How many hours?
    start = df.index[0].replace(minute=0, second=0)
    end = df.index[-1].replace(minute=0, second=0)
    for time in datespan(start, end):
        start = str(time)
        end = str(time.replace(minute59))
        datetime = time.strftime("%Y-%m-%d-%H")
        file = datetime + "-" + filename
        df.loc[start:end].to_csv(file, header=None)
    # duration = end-start
    # hours = duration.days*24 + duration.seconds // 3600
    # return hours

def averageDylos(df):
    df1 = pd.DataFrame()
    df1['0.5-DylosMean'] = (df['0.5-Dylos'] + df['0.5-Dylos2'])/2
    df1['2.5-DylosMean'] = (df['2.5-Dylos'] + df['2.5-Dylos2'])/2
    # df.drop(['0.5-Dylos', '2.5-Dylos', '0.5-Dylos2', '2.5-Dylos2'],  axis=1,  inplace = True)
    return df

def correlation(df):
    columns = ['0.23-Grimm', '0.3-Grimm', '0.4-Grimm', '0.5-Grimm', '0.65-Grimm', 
          '0.8-Grimm', '1-Grimm', '1.6-Grimm', '2-Grimm', '3-Grimm', '4-Grimm', 
          '5-Grimm', '7.5-Grimm', '10-Grimm', '15-Grimm', '20-Grimm']
    c = df.corr()['0.5-Dylos'][columns]
    print(c)
    c = df.corr()['2.5-Dylos'][columns]
    print(c)
    # s = c.unstack()
    # so = s.order(kind = "quicksort")
    # print(so)



