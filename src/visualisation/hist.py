#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import json
from utils import *
import logging

logging.basicConfig(filename='log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def histogram(df, bounds, plot_path, stats_path):
    """Plot a histogram of a binned data with defined bin boundaries.
    Args:
        df : Pandas.DataFrame
            Input dataframe with index of datetime object and each column is a
            bin od data
        bounds : list of floats
            List of bins boundaries.
        path : str
            Path for saved plots
    """
    # Initialise new series
    columns = ["lower", "upper", "width", "midpoint",
               "loglower", "logupper", "logwidth", "logmidpoint",
               'Counts', 'Cum Counts', 'Density', "dN/logD"]
    df1 = pd.DataFrame(columns=columns)

    # Take a mean of the input dataframe which becomes a series with column
    df1['Counts'] = df.mean(axis=0)
    totalCounts = df1['Counts'].sum()

    df1["lower"] = bounds[:-1]
    df1["upper"] = bounds[1:]
    df1["width"] = df1["upper"] - df1["lower"]
    df1["midpoint"] = df1["width"]/2 + df1["lower"]
    df1["loglower"] = np.log10(df1["lower"])
    df1["logupper"] = np.log10(df1["upper"])
    df1["logwidth"] = df1["logupper"] - df1["loglower"]
    df1["logmidpoint"] = np.log10(df1["midpoint"])
    df1["Density"] = df1["Counts"] / df1["width"]
    df1["dN/logD"] = df1["Counts"] / df1["logwidth"]

    # Iterate through the bins
    bins = df1.index
    cumCounts = 0
    for ix, key in enumerate(bins):
        counts = df1['Counts'].iloc[ix]
        lower = df1['lower'].iloc[ix]
        width = df1["width"].iloc[ix]

        # Cumulative frequency
        lowerCumCounts = cumCounts
        cumCounts += counts
        upperCumCounts = cumCounts
        df1['Cum Counts'].iloc[ix] = cumCounts

        # Median
        if lowerCumCounts < totalCounts/2 < upperCumCounts:
            median = lower + ((totalCounts/2 - lowerCumCounts)/counts) * width

    # Statistics
    counts = df1['Counts'].values
    midpoints = df1["midpoint"].values
    # logmidpoints = np.log10(midpoints)

    # Normal distribution
    mean, std, lower, upper = statistics(midpoints, counts)

    # Log normal distribution
    gm, gstd, glower, gupper = np.exp(statistics(np.log(midpoints), counts))

    # Sometimes a median is not found and so need to be excluded from display
    if 'median' in locals():
        index = ['Median',
                 'Mean Diameter', 'Std', '95% lower', '95% upper',
                 'Geometric mean diameter', 'Geometric standard deviation',
                 'Geometric 95% lower', 'Geometric 95% upper']
        statsdata = [median,
                     mean, std, lower, upper,
                     gm, std, glower, gupper]
    else:
        index = ['Mean Diameter', 'Std', '95% lower', '95% upper',
                 'Geometric mean diameter', 'Geometric standard deviation',
                 'Geometric 95% lower', 'Geometric 95% upper']
        statsdata = [mean, std, lower, upper,
                     gm, std, glower, gupper]

    statsdf = pd.DataFrame(statsdata, index=index)
    columns = ['Counts', 'Cum Counts', 'Density', 'dN/logD']

    if stats_path is not None:
        save_latex(statsdf, stats_path, "histstats", header=False)
        save_latex(df1[columns], stats_path, "histdata")

    if plot_path is not None:
        # Plot lognormal
        x1 = df1["lower"].tolist()  # left edge
        x2 = df1["upper"].tolist()  # right edge
        w = np.array(x2)-np.array(x1)  # variable width
        y = df1["dN/logD"].tolist()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.bar(x1, y, width=w)
        ax.set_xscale('log')
        plt.ylabel(r'Frequency per $\log \mu$')
        plt.xlabel(r'$\log \mathbf{Diameter}$ / $\mu$')
        saveplot(plot_path, fig)
        plt.close()


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("data", help="Date file")
    parser.add_argument("-p", "--plot",
                        help="Path to plot")
    parser.add_argument("-s", "--stats",
                        help="Path to statistics")
    parser.add_argument("-f", "--figsize",
                        help="Figure size")

    options = parser.parse_args()
    data_path = options.data
    plot_path = options.plot
    stats_path = options.stats
    fig_size = options.figsize

    msg = "Individual histogram of %s" % (data_path)
    logging.debug(msg)

    debug = "Data: %s, Plot: %s, Stats: %s" % (data_path, plot_path, stats_path)
    logging.debug(debug)

    # Set figure size
    if fig_size is not None:
        params = {"figure.figsize": figsize(float(fig_size))}
    else:
        params = {"figure.figsize": figsize(0.49)}
    matplotlib.rcParams.update(params)

    # load data
    df = load_data(data_path)

    # Fetch bin boundaries
    # Get path to settings json
    paths = os.path.normpath(data_path).split(os.path.sep)
    sensor = os.path.splitext(paths[-1])[0]
    path = os.path.sep.join(paths[:-3])
    filename = paths[-3] + ".json"
    path = os.path.join(path, filename)
    # Load setting file
    with open(path) as handle:
        settings = json.load(handle)
    # Grab bin boundaries of a sensor
    bounds = settings['sensors'][sensor]['bins']

    if plot_path is not None and stats_path is not None:
        # Plot histogram and get statistics
        histogram(df, bounds, plot_path, stats_path)
    else:
        raise ValueError("path not given for --plot or --stats")
