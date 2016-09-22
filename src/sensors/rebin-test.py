#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from src.modules.data import *
from src.modules.analysis import *
from grimm import rebinGrimm
from alpha import rebinAlpha
from datetime import datetime as dt
from copy import deepcopy


def test_rebin(path, old_bins, new_bins, name, rebinFunc):
    print(name)

    # load data
    bins = loadData(path, old_bins, name)

    # Print original data
    print("Original Data")
    print(bins['data'])

    print("Mean of original data")
    sum = bins['data'].sum()
    bins['sum'] = sum
    print(sum)
    print("Sum of sum of original data")
    print(sum.sum())

    # print("Statistics of original data")
    # midpoints = np.diff(bins['bounds'])/2 + bins['bounds'][:-1]
    # print(statistics(midpoints, meanOrig.values))
    # plotPath = plot(data, '.', "grimm")

    # Rebin
    ## Manual rebinning

    print("Manual rebinning")
    bins1 = deepcopy(bins)
    print("Input data")
    print(bins1['data'])
    rebinned = rebinFunc(bins1['data'])
    print("Output data")
    print(rebinned)
    print(rebinned.sum())
    print(rebinned.sum().sum())

    # Rebin
    del bins1
    print("Rebin algorithm")
    bins1 = deepcopy(bins)
    print("Input data")
    print(bins1['data'])
    rebinned = rebin(bins1, new_bins)
    print("Output")
    print(rebinned['data'])
    print(rebinned['data'].sum())
    print(rebinned['data'].sum().sum())

if __name__ == '__main__':

    # Grimm bins
    grimm_bins = ['', '', '', 0.5, 0.65, 0.8, 1, 1.6, 2, 3, 4, 5, 7.5, 10, '', '', '']

    # Alpha bins
    alpha_bins = [0.38, 0.54, 0.78, 1.05, 1.34, 1.59, 2.07, 3.0, 4.0, 5.0, 6.5, 8.0, 10.0, 12.0, 14.0, 16.0, 17.5]

    # New bin boundary
    new_bins = [0.5, 2.5, 10]

    # test data file
    path = "test-data.log"

    test_rebin(path, grimm_bins, new_bins, "grimm", rebinGrimm)

    test_rebin(path, alpha_bins, new_bins, "alpha", rebinAlpha)

