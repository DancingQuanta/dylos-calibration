#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Utility functions for data scripts

import os

def gen_bin_labels(binsList, string):
    """ Prepend a string to a list of bins boundaries to label each bin.
    Loop over bin boundaries list and if an element is an integer prepend
    given string to the integer and if not an integer leave an empty string
    in its place in list.

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
    newBinsList = []
    chosen_index = []

    for ix, val in enumerate(binsList):
        if isinstance(val, (int, float)):
            chosen_index = chosen_index + [ix]
            columns = columns + ["%s-%s" % (string, val)]
            newBinsList = newBinsList + [val]

    # Drop last element
    chosen_index = chosen_index[:-1]
    columns = columns[:-1]

    # Return dict of bin labels and bin value lists
    bins = {'columns': columns, 'bounds': newBinsList, 'index': chosen_index}
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

    # df.to_csv(path, header=True, index=True, index_label=df.index.name)
    df.to_csv(path)
    return path


def date_handler(obj):
    # Handles datetime object before json serialising it
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    # else:
        # raise TypeError



