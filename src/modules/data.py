#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Data manupulation for aerosols in the box.
Ensure you have install rebin module.

Sources of advice
http://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
"""

from operator import itemgetter
from itertools import groupby
import os
import sys
import numpy as np
import pandas as pd
import datetime as dt
from rebin import *


def date_handler(obj):
    # Handles datetime object before json serialising it
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    # else:
        # raise TypeError


def loadData(path, bins, string):
    """Load binned data into a Pandas.DataFrame where first column is datetime,
    each columns represent a bin and name each column according to a list of
    floats in argument.

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
    usecols = [0] + [x + 1 for x in binData['index']]

    # Load data
    df = pd.read_csv(path,
                     parse_dates={"Datetime": [0]},
                     index_col='Datetime',
                     infer_datetime_format=True,
                     header=None,
                     names=cols,
                     usecols=usecols)

    # Add data to bindata
    binData['data'] = df

    # Remove any empty string from columns
    binData['columns'] = [value for value in binData['columns']
                          if not value == ""]

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
    newBinsList = []
    chosen_index = []

    for ix, val in enumerate(binsList):
        if isinstance(val, (int, float)):
            chosen_index = chosen_index + [ix]
            columns = columns + ["%s-%s" % (string, val)]
            stringBins = stringBins + ["%s/ " % (val)]
            newBinsList = newBinsList + [val]

    # Drop last element
    chosen_index = chosen_index[:-1]
    columns = columns[:-1]
    stringBins = stringBins[:-1]

    # Return dict of bin labels and bin value lists
    bins = {'columns': columns, 'stringbins': stringBins,
            'bounds': newBinsList, 'index': chosen_index}
    return bins


def writeData(df, path, filename):
    """Write Pandas.DataFrame to csv file
    Args:
        df: Pandas.DataFrame
        path: string
            Path to location of file
        filename: str
            Name of the file
    Returns: None
    """
    filename = filename + ".csv"
    path = os.path.join(path, filename)
    df.to_csv(path)
    return path


def continuousFill(data):
    """Fill missing time series data of a Pandas.DataFrame with NaN at minute
    interval
    """
    date_index = data.index
    new_index = pd.date_range(min(date_index), max(date_index), freq='T')
    data = data.reindex(new_index)
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
        if len(ranges) != 0:
            start,  end = zip(* ranges)
            startdt = data.index[list(start)]
            enddt = data.index[list(end)]
            dict = {"Startx": start, "Endx": end,
                    "Startdt": startdt, "Enddt": enddt}
            list = ["Startx", "Endx", "Startdt", "Enddt"]
            df = pd.DataFrame(dict, columns=list)
            return df
        else:
            print("No Nan")
            return None
    except Exception as e:
        print(e)
        return None


def segments(data, path, name):
    """
    Group non-null values into segments and write them to file
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
        if len(ranges) != 0:
            start,  end = zip(* ranges)
            startdt = data.index[list(start)]
            enddt = data.index[list(end)]
            dict = {"Startx": start, "Endx": end,
                    "Startdt": startdt, "Enddt": enddt}
            list = ["Startx", "Endx", "Startdt", "Enddt"]
            df = pd.DataFrame(dict, columns=list)
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
    """Concatenate two Pandas.DataFrames together.
    The first dataframe's index will be used to set the index of second if the
    length of the indexes are equal.
    Different length dataframes can be concatanced together, where the shorted
    index is used.
    """
    if len(df1) == len(df2):
        print("Same")
        df2.index = df1.index
        df = df1.join(df2)
    elif len(df1) > len(df2):
        print("df1 big")
        start = df2.index[0]
        end = df2.index[-1]
        df3 = df1.loc[start:end]
        df = df3.join(df2)
    elif len(df1) < len(df2):
        print("df2 big")
        start = df1.index[0]
        end = df1.index[-1]
        df3 = df2.loc[start:end]
        df = df1.join(df3)
    else:
        error = "Something not right!"
        print(error)
        sys.exit(2)
    return df


def realCounts(data):
    """Subtract the upper bins from the lower bins
    """
    # Get number of columns, loop over, sum upper and subtract from lower.
    columns = data.columns
    for i in range(0, len(columns)):
        sumup = data[columns[(i+1):]].sum(axis=1)
        data[columns[i]] = data[columns[i]] - sumup
    return data


def pruneBins(data):
    """Drop bins if they have zero counts in the mean.

    Args:
        data : dict
            Input dict with three key-value pairs; 'columns', 'bounds' and
            'data'.
            Value of 'columns' is list of strings of labels of bin columns
            which is {sensor name}-{lower bin boundary}

            Value of 'bounds' is list of low bin boundary positions, with the
            last element being the top boundary of last bin.

            Value of 'data' is Pandas.DataFrame where the column labels are
            same as 'columns'

    Returns:
        data; dict
            The output will have same structure as input dict.
            The dataframe will have fewer columns, and the list of bin
            boundaries would be shorter.

    """
    df = data['data']
    # Initialise new dataframe
    df1 = pd.DataFrame(columns=['Counts'])
    df1['Counts'] = df.mean(axis=0)
    binsList = df1.index
    zeroColumns = []
    for ix, key in enumerate(binsList):
        counts = np.round(df1['Counts'].iloc[ix])
        # Do not want to display histogram of bins at large sizes if
        # the counts is zero.
        if counts == 0:
            zeroColumns = zeroColumns + [ix]
        elif counts > 0:
            zeroColumns = []

    # Drop columns using zeroColumns
    df = df.drop(df.columns[zeroColumns], axis=1)
    prunedColumns = df.columns
    data['columns'] = prunedColumns
    data['bounds'] = data['bounds'][:len(prunedColumns)+1]
    data['data'] = df
    return data


def rebin(bins1, bins2):
    """Rebin binned data to new bin boundaries.
    Uses the rebin_piecewise_constant function from jhykes/rebin github repo.

    Args:
        bins1 : dict of str: list, str: list, str: Pandas.DataFrame
            Input dict with three key-value pairs; 'columns', 'bounds' and
            'data'.

            Value of 'columns' is list of strings of labels of bin columns
            which is {sensor name}-{lower bin boundary}

            Value of 'bounds' is list of low bin boundary positions, with the
            last element being the top boundary of last bin.

            Value of 'data' is Pandas.DataFrame where the column labels are
            same as 'columns'
        bins2 : list of int
            The list is the low bin boundary positions, with the
            last element being the top boundary of last bin.
            This list will be used to rebin the 'data' in bins1

    Return:
        bins2: dict of str: list, str: Pandas.DataFrame
            Output dict with same structure as bins1 but with newly changed
            bins bounbaries

    """

    # Generate bin labels for final set of bins
    # but first extract the string before dash in column names of initial data.
    string = bins1['columns'][0].split('-')
    label = string[0]
    bins2 = generateBinLabels(bins2, label)

    # Ensure the lower boundary of lowest bin and upper boundary of
    # highest bin of new bin list is within the limits of old bin list
    if bins2['bounds'][0] < bins1['bounds'][0]:
        msg = ("The lower boundary of new bottommost bin (%s)"
               "is lower then the lower boundary of old mottommost"
               "bin (%s)" % (bins2['bounds'][0], bins1['bounds'][0]))
        raise ValueError(msg)
    if bins2['bounds'][-1] > bins1['bounds'][-1]:
        msg = ("The upper boundary of new topmost bin (%s)"
               "is higher then the upper boundary of old topmost"
               "bin (%s)" % (bins2['bounds'][-1], bins1['bounds'][-1]))
        raise ValueError(msg)

    # Assign bin boundaries
    x1 = np.array(bins1['bounds'])
    x2 = np.array(bins2['bounds'])

    # Check if input data is a series or dataframe
    if isinstance(bins1['data'], pd.Series):
        y1 = bins1['data'].values
        y2 = rebin_piecewise_constant(x1, y1, x2)
        # Initialise new dataframe
        bins2['data'] = pd.Series(y2, index=bins2['columns'])
    elif isinstance(bins1['data'], pd.DataFrame):
        index = bins1['data'].index
        columns = bins2['columns']
        # Initialise new dataframe
        bins2['data'] = pd.DataFrame(0, index=index, columns=columns)
        for ix in index:
            y1 = bins1['data'].loc[ix].values
            y2 = rebin_piecewise_constant(x1, y1, x2)
            bins2['data'].loc[ix] = y2

    return bins2
