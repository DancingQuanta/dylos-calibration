#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Helper functions for Grimm Aerosol spectrometer

from modules.tools import *

def loadGrimmData(path):
    columns = ['0.23-Grimm', '0.3-Grimm', '0.4-Grimm', '0.5-Grimm', '0.65-Grimm',
          '0.8-Grimm', '1-Grimm', '1.6-Grimm', '2-Grimm', '3-Grimm', '4-Grimm',
          '5-Grimm', '7.5-Grimm', '10-Grimm', '15-Grimm', '20-Grimm']
    df = loadData(path, columns)
    return df

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

