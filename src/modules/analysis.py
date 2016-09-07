#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Plotting helper functions

"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def nmoment(x, counts, c, n):
    return np.sum(((x-c)**n)*counts) / np.sum(counts)

def stats(midpoints, counts):
    """Statistics for binned data

    Args:
        counts: ndarray
        midpoints: adarray

    Returns:

    """
    totalCounts = np.sum(counts)
    # Mean
    mean = nmoment(midpoints, counts, 0, 1)

    # Standard deviation
    std = nmoment(midpoints, counts, mean, 2)

    # Lower 95% bounds
    lower = mean - 2 * std

    # Upper 95% bounds
    upper = mean + 2 * std

    return mean, std, lower, upper


def histstd(data, bounds, mean):
    """Calculate standard deviation of a binned data
    Args:
        data : list
            list of counts per bin
        bins : list
            list of bin boundaries, with length one element longer than data
        mean : float

    Returns:
        std : float
            Standard deviation
    """
    numerator = 0
    totalCounts = 0
    for ix, key in enumerate(data):
        counts = data[ix]
        lower = bounds[ix]
        upper = bounds[ix+1]
        difference = upper-lower
        midpoint = lower + difference/2
        totalCounts = totalCounts + counts
        numerator = counts * ((midpoint - mean) ** 2) + numerator

    denominator = totalCounts
    std = np.sqrt(numerator / denominator)
    return std, lower, upper


def normalise(data, bins):
    for key in bins:
        value = bins[key]
        if isinstance(value,  tuple):
            if len(value) == 2:
                lower = value[0]
                upper = value[1]
                difference = upper-lower
                data[key] = data[key]/difference
            else:
                error = "The length of value of the key %s is %s,  must be 2" % (key, len(value))
                print(error)
        else:
            error = "The type of value of the key %s is %s,  must be tuple e.g. (1, 2)" % (key, type(value))
            print(error)
    return data


def geometricStd(data, bounds, gmd):
    """Calculate geometric standard deviation of a lognormal distribution
    Args:
        data : list
            list of counts per bin
        bins : list
            list of bin boundaries, with length one element longer than data
        gmd : float
            Geometric mean diameter

    Returns:
        gsd : float
            Geometric standard deviation
    """
    # Geometric standard deviation
    numerator = 0
    totalCounts = 0
    for ix, key in enumerate(data):
        counts = data[ix]
        lower = bounds[ix]
        upper = bounds[ix+1]
        difference = upper-lower
        midpoint = lower + difference/2
        logmidpoint = np.log10(midpoint)  # Is this correct? todo
        totalCounts = totalCounts + counts
        numerator = counts * ((logmidpoint - np.log10(gmd)) ** 2) + numerator

    denominator = totalCounts - 1
    loggsd = np.sqrt(numerator / denominator)
    gsd = np.exp(loggsd)

    # Lower 95% bounds
    lower = gmd / (gsd ** 2)

    # Upper 95% bounds
    upper = gmd * (gsd ** 2)

    return gsd, lower, upper


def plot(data, path, name):
    filename = name + "-plot.pdf"
    path = os.path.join(path, filename)
    print("Plotting: %s" % (path))
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    data.plot(ax=ax)
    plt.ylabel('Particle count')
    plt.xlabel('Time')
    plt.tight_layout()
    fig.savefig(path)
    plt.clf()
    # plt.close()
    return path.replace("\\", "/")


def histogram(data, path, name):
    """Plot a histogram of a binned data with defined bin boundaries.
    Args:
        df : Pandas.DataFrame
            Input dataframe with index of datetime object and each column is a
            bin od data
        bounds : list of floats
            List of bins boundaries.
        path : str
            Path for saved plots

    Returns:
        dataDict: dict
            dictionary of plots paths, statistics
    """

    # Load data
    df = data['data']
    bounds = data['bounds']

    # Initialise new dict for data output
    dataDict = {}
    dataDict['histplot'] = {}

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
    mean, std, lower, upper = stats(midpoints, counts)

    # Log normal distribution
    gm, gstd, glower, gupper = np.exp(stats(np.log(midpoints), counts))

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

    statistics = pd.DataFrame(statsdata, index=index)
    statslatex = statistics.to_latex(header=False)
    columns = ['Counts', 'Cum Counts', 'Density']

    datalatex = df1[columns].to_latex()
    dataDict['histstats'] = statslatex
    dataDict['histdata'] = datalatex

    # Plots
    x1 = df1["lower"].tolist()  # left edge
    x2 = df1["upper"].tolist()  # right edge
    w = np.array(x2)-np.array(x1)  # variable width
    y = df1['Density'].tolist()

    plt.clf()
    fig = plt.figure()
    plt.bar(x1, y, width=w)
    plt.ylabel(r'Frequency per $\mu$$')
    plt.xlabel(r'\textbf{Diameter} / $\mu$')
    filename1 = name + "-hist.pdf"
    path1 = os.path.join(path, filename1)
    dataDict['histplot']["hist"] = path1.replace("\\", "/")
    fig.savefig(path1)

    # Cumulative distribution
    y = df1['Cum Counts'].tolist()

    plt.clf()
    fig = plt.figure()
    plt.plot(x1, y)
    plt.ylabel(r'Cumulative frequency')
    plt.xlabel(r'\textbf{Diameter} / $\mu$')
    filename1 = name + "-cumFreq.pdf"
    path1 = os.path.join(path, filename1)
    dataDict['histplot']["cumFreq"] = path1.replace("\\", "/")
    fig.savefig(path1)

    # x1 = df1["loglower"].tolist() # left edge
    # x2 = df1["logupper"].tolist() # right edge
    # w = np.array(x2)-np.array(x1) # variable width
    y = df1["dN/logD"].tolist()
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x1, y, width=w)
    ax.set_xscale('log')
    # ax.set_yscale('log')
    plt.ylabel(r'Frequency per $\log \mu$')
    plt.xlabel(r'$\log \mathbf{Diameter}$ / $\mu$')

    filename2 = name + "-histlog.pdf"
    path2 = os.path.join(path, filename2)
    dataDict['histplot']["histlog"] = path2.replace("\\", "/")
    fig.savefig(path2)
    plt.clf()
    return dataDict


def plot_corr(df, plotspath, statspath, name, size=14):
    """Function plots a graphical correlation matrix for each pair
    of columns in the dataframe.

    Args:
        df (Pandas.DataFrame):
        path (str): Path for figure to be saved to.
        size (int): vertical and horizontal size of the plot
    """
    # Correlation analysis
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(corr)
    locs, labels = plt.xticks(range(len(corr.columns)), corr.columns)
    plt.setp(labels, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    filename = name + "-corr.pdf"
    path = os.path.join(plotspath, filename)
    fig.savefig(path)
    print("Saved correlations graph")
    plt.clf()

    # corr[corr<threshold] = np.nan
    # corr.fillna(0, inplace = True)
    filename = name + "-corr.csv"
    path = os.path.join(statspath, filename)
    corr.to_csv(path)

    # Covariance analysis
    cov = df.cov()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(cov)
    locs, labels = plt.xticks(range(len(cov.columns)), cov.columns)
    plt.setp(labels, rotation=90)
    plt.yticks(range(len(cov.columns)), cov.columns)
    filename = name + "-cov.pdf"
    path = os.path.join(plotspath, filename)
    fig.savefig(path)
    print("Saved covariations graph")


def make_scatter_plot(df, path, name):
    """
    Make scatterplot of a dataframe

    Args:
        df (Pandas.DataFrame):
        path (str): Path for figure to be saved to.

    """
    plt.clf()
    fig = plt.figure()
    axs = pd.scatter_matrix(df, alpha=0.2)
    for ax in axs[:, 0]:  # the left boundary
        ax.grid('off', axis='both')
        # ax.set_yticks([0, .5])

    for ax in axs[-1, :]:  # the lower boundary
        ax.grid('off', axis='both')
        # ax.set_xticks([0, .5])
    filename = name + "-scatter-matrix.pdf"
    path = os.path.join(path, filename)
    fig.savefig(path)


def scatter_matrix(df, path, name):
    filename = name + "-scatter-matrix.pdf"
    path = os.path.join(path, filename)

    fig, axarr = plt.subplots(4, 4, sharex=True)

    x = df.columns[0]
    print(x)
    for i, ax in enumerate(fig.axes):
        y = df.columns[i + 2]
        print(y)
        df.plot(x=x, y=y, ax=ax, kind='scatter')

    # # the left boundary
    # axarr[:, 0].grid('off', axis='both')
    # axarr[:, 0].set_yticks([0, .5])

    # # the lower boundary
    # axarr[-1, :].grid('off', axis='both')
    # axarr[-1, :].set_xticks([0,  .5])
    fig.savefig(path)


def scatter_plot(df, path, name):
    filename = name + "-scatter.pdf"
    path = os.path.join(path, filename)
    for x in df.columns:
        for y in df.columns:
            df.plot(x=x, y=y, kind='scatter')
            filename = "%s_%s_%s" % (x, y, name)
            plt.savefig(os.path.join(path, filename))


def compare(data, path):
    plot_corr(data, path)
    # scatter_plot(data, path)
