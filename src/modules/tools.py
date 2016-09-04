#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Data Analysis for aerosol sensors in a box

Sources of advice
http://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
"""

from operator import itemgetter
from itertools import groupby
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.tools.plotting import scatter_matrix
import datetime as dt
matplotlib.style.use('ggplot')
pd.options.display.float_format = '{:.2f}'.format

def loadData(path, bins, string):
    """Load binned data into a Pandas.DataFrame where first column is datetime,
    each columns represent a bin and name each column according to a list of
    floats in argument.

    # Define list of indexes to select columns to load based on columns list
    # given in arguments.
    # Elenents containing empty string will be ignored and an list of indexes
    # of non-empty string will be built and used to select columns to load.

    Args:
        path : string
            path to datafile
        bins : list
        List of floats of bin boundaries, where every except the last element
        represent lower bin boundary and the last is uppper bin boundary of the
        last bin.
    Returns:
        df: Pandas.DataFrame

    """
    # Use list of bin boundaries to generate a list of bin labels for the
    # DataFrame
    binData = generateBinLabels(bins, string)

    # Set the labels of DataFrame columns
    # Generate indexes of elements in columns to load, if any element is an
    # empty string do not include its index.
    cols = ['DateTime'] + binData['columns']
    usecols = [index for index, value in enumerate(cols)
                     if not value == ""]

    # Load data
    try:
        df = pd.read_csv(path,
                         parse_dates={"Datetime": [0]},
                         index_col='Datetime',
                         infer_datetime_format=True,
                         header=None,
                         names=cols,
                         usecols=usecols)
    except Exception as e:
        print(e)
        sys.exit(2)

    # Add data to bindata
    binData['data'] = df

    # Remove any empty string from columns
    columns = [value for value in columns if not value == ""]
    binData['columns'] = columns

    # Return the dict
    return binData


def generateBinLabels(binsList, string):
    """ Prepend a string to a list of bins boundaries to label each bin.
    Loop over bin boundaries list and if an element is an integer prepend
    given string to the integer and if not an integer leave an empty string
    in its place in list.
    Also create another list of bin boundaries with slashes for display.

    Args:
        binsList: list of ints
            list of lower bin boundaries with last element being upper
            boundary of last bin.
        string: str
            string to be prepanded, ideally name of sensor

    Returns:
        bins: dict
            The dict contain three key-values pair; columns, bounds,
            stringbins.
            columns key is for labelling Pandas DataFrame columns
            bounds is the bin boundaries list minus any empty element.
            stringbins is the bin boundaries as string for display

    """
    columns = []
    stringBins = []
    for key in binsList[:-1]:
        if isinstance(key, (int, float)):
            columns = columns + ["%s-%s" % (string, key)]
            stringBins = stringBins + ["%s/ " % (key)]
        else:
            columns = columns + [""]

    # Remove any non-integer elements
    binsList = [key for key in binsList
                if isinstance(key, (int, float))]

    # Return dict of bin labels and bin value lists
    bins = {'columns': columns, 'bounds': binsList, 'stringbins': stringBins}
    return bins


def writeData(df, path, filename):
    """Write Pandas.DataFrame to file
    Args:
        df: Pandas.DataFrame
        path: string
            Path to location of file
        filename: str
            Name of the file
    Returns: None
    """
    filename = filename + ".csv"
    path = os.path.join(dataPathGen(path), filename)
    df.to_csv(path)


def continuousFill(data):
    """Fill missing time series data of a Pandas.DataFrame with NaN at minute
    interval
    """
    date_index = data.index
    data = data.reindex(pd.date_range(min(date_index), max(date_index), freq='T'))
    return data


def findGroups(index):
    """
    Find group of consective sequence
    """

    ranges = []
    for k, g in groupby(enumerate(index), lambda ix: ix[1]-ix[0]):
        group = list(map(itemgetter(1), g))
        ranges.append((group[0], group[-1]))
    return ranges


def findGaps(data):
    """
    Find null values and group them
    """
    try:
        if isinstance(data,  pd.DataFrame):
            ts = data[data.columns[0]]
        else:
            ts = data

        # Fill missing data with NaNs 
        ts = ts.reindex(pd.date_range(min(ts.index), max(ts.index), freq='T'))

        index = np.where(ts.isnull())[0]
        ranges = findGroups(index)
        if len(ranges) !=  0:
            start,  end = zip(* ranges)
            startdt = data.index[list(start)]
            enddt = data.index[list(end)]
            df = pd.DataFrame({"Startx": start, "Endx": end,
                              "Startdt": startdt, "Enddt": enddt},
                             columns=["Startx", "Endx", "Startdt", "Enddt"])
            return df
        else:
            print("No Nan")
            return None
    except Exception as e:
        print(e)
        return None

def segments(data, path, name):
    """
    Group non-null values into segments
    """
    try:
        if isinstance(data,  pd.DataFrame):
            ts = data[data.columns[0]]
        else:
            ts = data

        # Fill missing data with NaNs 
        ts = ts.reindex(pd.date_range(min(ts.index), max(ts.index), freq='T'))

        index = np.where(ts.notnull())[0]
        ranges = findGroups(index)
        if len(ranges) !=  0:
            start,  end = zip(* ranges)
            startdt = data.index[list(start)]
            enddt = data.index[list(end)]
            df = pd.DataFrame({"Startx": start, "Endx": end,
                              "Startdt": startdt, "Enddt": enddt},
                             columns=["Startx", "Endx", "Startdt", "Enddt"])
            for i in range(0, len(ranges)):
                segment = data.iloc[start[i]:(end[i]+1)]
                startdt = segment.index[0].strftime("%Y-%m-%d_%H-%M-%S")
                enddt = segment.index[-1].strftime("%Y-%m-%d_%H-%M-%S")
                filename = "%s_%s_%s" % (startdt, enddt, name)
                path1 = os.path.join(path, filename)
                segment.to_csv(path1, header=None)
            return df
        else:
            print("All Nan!")
            return None
    except Exception as e:
        print(e)
        return None

def datespan(startDate, endDate, delta=dt.timedelta(hours=1)):
    curDate = startDate
    while curDate < endDate:
        yield curDate
        curDate += delta

def difference(df):
    diff = df.index[-1] - df.index[0]
    return diff

def concat(df1, df2):
    if len(df1) == len(df2):
        df2.index = df1.index
        df = df1.join(df2)
    elif len(df1) > len(df2):
        start = df2.index[0]
        end = df2.index[-1]
        df3 = df1.loc[start:end]
        df = df3.join(df2)
    elif len(df1) < len(df2):
        start = df1.index[0]
        end = df1.index[-1]
        df3 = df2.loc[start:end]
        df = df1.join(df3)
    else:
        error = "Something not right!"
        print(error)
        sys.exit(2)
    return df

def changeExt(path, ext):
    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]+ext
    return filename

def pathGen(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def dataPathGen(path):
    path = os.path.join(path, "data")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def statsPathGen(path):
    path = os.path.join(path, "stats")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def plotsPathGen(path):
    path = os.path.join(path, "plots")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def date_handler(obj):
    # Handles datetime object before json serialising it
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    # else:
        # raise TypeError


def realCounts(data):
    # Get number of columns,  loop over,  sum upper and subtract from lower
    columns = data.columns
    for i in range(0, len(columns)):
        sumup = data[columns[(i+1):]].sum(axis=1)
        data[columns[i]] = data[columns[i]] - sumup
    return data

def pruneBins(data):
    """Drop bins if they have zero counts in the mean.

    Args:
        data : dict
            This dictionary must contain at least the Panda.DataFrame of binned
            data and a list of floats of bin boundaries.
            The DataFrame have index of datetime object and each column is a
            bin od data.

    Returns:
        df : Pandas.DataFrame
            Output copy of Input dataframe minus dropped bins
        newBins : dict of str: tuple
            Outpuf dict of column labels and bin boundaries

    """
    df = data['data']
    bounds = data['bounds']
    # Initialise new dataframe
    df1 = pd.DataFrame(columns = ['Counts'])
    df1['Counts'] = df.mean(axis=0)
    binsList = df1.index
    for ix, key in enumerate(binsList):
        counts = np.round(df1['Counts'].iloc[ix])
        # Do not want to display histogram of bins at large sizes if
        # the counts is zero.
        if counts == 0:
            zeroColumns = zeroColumns + [ix]
        elif counts > 0:
            zeroColumns = []

    # Drop columns using zeroColumns
    df = df.drop(df.columns[zeroColumns],axis=1)
    prunedColumns = df.columns
    data['columns'] = prunedColumns
    data['bounds'] = data['bounds'][:len(prunedColumns)+1]
    data['data'] = df

    # prunedColumns = [key for key in binsList if key not in zeroColumns]
    # prunedBounds = bounds[:len(prunedColumns)+1]
    # prunedBins = {'columns': prunedColumns, 'bounds': prunedBounds}
    return data


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

def twoPlots(df1, df2, path, name):
    filename = name + "-2plot.pdf"
    path = os.path.join(path, filename)
    print("Plotting two plots: %s" % (path))
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    df1.plot(ax=ax)
    df2.plot(ax=ax)
    plt.ylabel('Particle count')
    plt.xlabel('Time')
    plt.legend(loc='upper right')
    plt.tight_layout()
    fig.savefig(path)

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
        lower = midpoints[ix]
        upper = bounds[ix+1]
        difference = upper-lower
        midpoint = lower + difference/2
        totalCounts = totalCounts + counts
        numerator = counts * ((midpoint - mean) ** 2) + numerator

    denominator = totalCounts
    std = np.sqrt(numerator / denominator)


    return std, lower, upper

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
        logmidpoint = np.log10(midpoint) # Is this correct? todo
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


def stats(counts, midpoints):
    """Statistics for binned data

    Args:
        counts: ndarray
        midpoints: adarray

    Returns:

    """
    # Totoal counts
    totalCounts = np.sum(counts)

    # Mean
    mean = np.sum(counts * midpoints) / totalCounts

    # Standard deviation
    std = np.sum(counts * ((midpoints - mean) ** 2)) / totalCounts

    # Lower 95% bounds
    lower = mean - 2 * std

    # Upper 95% bounds
    upper = mean + 2 * std

    return mean, std, lower, upper


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

        # Cumulative frequency
        lowerCumCounts = cumCounts
        cumCounts += counts
        upperCumCounts = cumCounts
        df1['Cum Counts'].iloc[ix] = cumCounts

        # Median
        if lowerCumCounts < totalCounts/2 < upperCumCounts:
            median = df1['lower'].iloc[ix] + ((totalCounts/2 - lowerCumCounts)/counts) * df1["width"].iloc[ix]

    # Statistics
    counts = df1['Counts'].values
    midpints = df1["midpoint"].values
    midpoints = np.diff(bounds)/2 + bounds[:-1]
    logmidpoints = np.log10(midpoints)

    # Normal distribution
    mean, std, lower, upper = stats(counts,midpoints)

    # Log normal distribution
    gm, gstd, glower, gupper = np.exp(stats(counts, np.log(midpoints)))

    # Sometimes a median is not found and so need to be excluded from display
    if 'median' in locals():
        # statistics = {'Median': median,
                      # 'Mean Diameter': mean, 'Std': std, '95% lower': lower, '95% upper': upper,
                      # 'Geometric mean diameter': gm, 'Geometric standard deviation': gstd,
                      # 'Geometric 95% lower': glower, 'Geometric 95% upper': gupper}
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
    x1 = df1["lower"].tolist() # left edge
    x2 = df1["upper"].tolist() # right edge
    w = np.array(x2)-np.array(x1) # variable width
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

def compare(data, path):
    plot_corr(data, path)
    make_scatter_plot(data, path)
    # scatter_plot(data, path)

def analyse(data,savepath,filename):
    """Plot input data and subtract the larger sizes from smaller sizes.
    Also print the input data to file for diagonistics purposes.

    """

    print(filename)
    writeData(data,savepath,filename)
    plot(data,savepath,filename)
    realData = realCounts(data)
    filename = "real_" + filename
    writeData(data,savepath,filename)
    plot(realData,savepath,filename)
    return realData

def plot_corr(df, path, size=14):
    """
    Function plots a graphical correlation matrix for each pair of columns in the dataframe.

    Args:
        df (Pandas.DataFrame):
        path (str): Path for figure to be saved to.
        size (int): vertical and horizontal size of the plot
    """
    # Create paths to plots and stats if necessary and fetch their paths
    stats = statsPathGen(path)
    plots = plotsPathGen(path)

    # Correlation analysis
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(corr)
    locs, labels = plt.xticks(range(len(corr.columns)), corr.columns)
    plt.setp(labels, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    filename = changeExt(path, "-corr.pdf")
    fig.savefig(os.path.join(plots, filename))
    print("Saved correlations graph")
    plt.clf()

    # corr[corr<threshold] = np.nan
    #corr.fillna(0, inplace = True)
    filename = changeExt(path, "-corr.csv")
    corr.to_csv(os.path.join(stats, filename))

    # Covariance analysis
    cov = df.cov()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(cov)
    locs, labels = plt.xticks(range(len(cov.columns)), cov.columns) # Replace cov with corr if not working
    plt.setp(labels, rotation=90)
    plt.yticks(range(len(cov.columns)), cov.columns)
    filename = changeExt(path, "-cov.pdf")
    fig.savefig(os.path.join(plots, filename))
    print("Saved covariations graph")

def make_scatter_plot(df, path):
    """
    Make scatterplot of a dataframe

    Args:
        df (Pandas.DataFrame):
        path (str): Path for figure to be saved to.

    """
    plt.clf()
    fig = plt.figure()
    axs = pd.scatter_matrix(df, alpha=0.2)
    for ax in axs[:, 0]: # the left boundary
        ax.grid('off', axis='both')
        #ax.set_yticks([0, .5])

    for ax in axs[-1, :]: # the lower boundary
        ax.grid('off', axis='both')
        #ax.set_xticks([0, .5])
    filename = changeExt(path, "-scatter-matrix.pdf")
    path = os.path.join(plotsPathGen(path), filename)
    fig.savefig(path)

def scatter_matrix(df, path):
    fig, axarr = plt.subplots(4, 4, sharex=True)

    x = df.columns[0]
    print(x)
    for i, ax in enumerate(f.axes):
        y = df.columns[i + 2]
        print(y)
        df.plot(x=x, y=y, ax=ax, kind='scatter')

    # # the left boundary 
    # axarr[:, 0].grid('off', axis='both')
    # axarr[:, 0].set_yticks([0, .5])

    # # the lower boundary
    # axarr[-1, :].grid('off', axis='both')
    # axarr[-1, :].set_xticks([0,  .5])
    filename = changeExt(path, "-scatter-matrix.pdf")
    path = os.path.join(plotsPathGen(path), filename)
    fig.savefig(path)

def scatter_plot(df, path):
    name = changeExt(path, "-scatter.pdf")
    plots = plotsPathGen(path)
    for x in df.columns:
        for y in df.columns:
            df.plot(x=x, y=y, kind='scatter')
            filename = "%s_%s_%s" % (x, y, name)
            plt.savefig(os.path.join(plots, filename))

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

