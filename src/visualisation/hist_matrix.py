#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import argparse
import json
from collections import OrderedDict
from utils import *
import logging
import pprint

logging.basicConfig(filename='log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def histogram(df, bounds, ax):
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

    stats_dict = OrderedDict({'gmd': gm, 'gstd': gstd,
                  'glower': glower, 'gupper': gupper})

    index = ['Geometric mean diameter', 'Geometric standard deviation',
             'Geometric 95% lower', 'Geometric 95% upper']
    statsdata = [gm, std, glower, gupper]
    statsdf = pd.DataFrame(statsdata, index=index)

    # Plot lognormal
    x1 = df1["lower"].tolist()  # left edge
    x2 = df1["upper"].tolist()  # right edge
    w = np.array(x2)-np.array(x1)  # variable width
    y = df1["dN/logD"].tolist()
    ax.bar(x1, y, width=w)
    ax.set_xscale('log')

    return stats_dict

    # save_latex(statsdf, stats_path, "histstats", header=False)


def table(dictionary):
    try:
        # Reform dictionary into multiindex compatible dict
        reform = {(conditions_key, sensors_key, stats_key): [values]
                  for conditions_key, sensors_dict in dictionary.items()
                  for sensors_key,    stats_dict   in sensors_dict.items()
                  for stats_key,      values       in stats_dict.items()}
        logging.debug(pprint.pformat(reform))
        # Create Multiindex DataFrame and transpose it
        df = pd.DataFrame(reform)
        df = df.T
        # Set names of indexes
        names = [r'Particle size/\si{um}', 'Sensors', '']
        df.index.set_names(names, inplace=True)
        logging.debug(df)
        # Make statistics columns
        unstack = df.unstack()
        logging.debug(unstack)
        # Rename columns
        rename = {'gmd':    'Geometric Mean Diameter',
                  'gstd':   'Geometric STD',
                  'glower': 'Geometric lower 95%',
                  'gupper': 'Geometric upper 95%'}
        unstack = unstack.rename(columns=rename)
        logging.debug(unstack)
        order = ['Geometric mean diameter', 'Geometric standard deviation',
                 'Geometric lower 95%', 'Geometric upper 95%']
    except:
        logging.exception('Got exception on main handler')
        raise


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Date file")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")

    options = parser.parse_args()
    settings_file = options.settings
    output_file = options.output

    msg = "Histogram matrix of %s" % (settings_file)
    logging.debug(msg)

    # Load settings yaml file
    with open(settings_file) as handle:
        settings = json.load(handle)

    # Load sensor info
    calibrater = settings['calibration']['calibrater']
    calibratee = settings['calibration']['calibratee']
    rebinned = settings['calibration']['rebinned']
    sensors = settings['sensors']

    # Experimental conditions
    exps = settings['exp']

    # Conditions
    exp_order = exps['order']
    conditions = exps['conditions']

    # Matrix dimension
    nrows=len(exp_order)
    ncols=3

    # Fig size
    fig_width = 2
    golden_mean = (np.sqrt(5.0)-1.0) / 2.0
    fig_height = fig_width * golden_mean
    width_ratios = [0.5] + ncols * [1]
    fig_size = [(fig_width * sum(width_ratios)), (fig_height * nrows)]

    # Create matrix with first columns for particles
    fig = plt.figure(figsize=fig_size)
    gs = gridspec.GridSpec(nrows, (ncols + 1),
                           width_ratios=width_ratios,
                           wspace=0.5, hspace=0.10)

    x_label = r'Diameter / \si{\um}'
    y_label = r'Frequency per $\log D$'

    # First column
    ax = plt.subplot(gs[0, 0])
    ax.set_title(exps['parameter'])
    ax.annotate(y_label, xy=(1, 0.5),
                xycoords=('axes fraction', 'figure fraction'),
                xytext=(10, 0),
                textcoords='offset points',
                ha='center', va='center',
                rotation='vertical')

    msg = "Looping over conditions"
    logging.debug(msg)

    exp_stats_dict = {}
    exp_stats = pd.DataFrame(index=exp_order)
    exp_stats.index.name = exps['parameter']

    for i, exp in enumerate(exp_order):
        msg = ("Index: %s, Condition: %s, "
               "Calibrater: %s, Calibratee: %s") % (i, exp, calibrater,
                                                    calibratee)
        logging.debug(msg)
        condition = conditions[exp]
        # Get name
        y_title = condition['parameter']

        # First column
        ax1 = plt.subplot(gs[i, 0])
        ax1.annotate(y_title, xy=(0.5, 0.5),
                     xycoords=('axes fraction', 'axes fraction'),
                     xytext=(0, 0),
                     textcoords='offset points',
                     size=11, ha='center', va='bottom')
        ax1.axis('off')

        # Second column
        # load calibratee data and plot it!
        data_path = condition['sensor'][calibratee]['data']
        df = load_data(data_path)

        # Get bins
        bounds = sensors[calibratee]['bins']

        # Pick an axes
        ax2 = plt.subplot(gs[i, 1])

        # Histogram logdensity
        hist1 = histogram(df, bounds, ax2)
        ax2.xaxis.set_visible(False)

        # Third column
        # load calibrater data and plot it!
        data_path = condition['sensor'][calibrater]['data']
        df = load_data(data_path)

        # Get bins
        bounds = sensors[calibrater]['bins']

        # Pick an axes
        ax3 = plt.subplot(gs[i, 2])

        # Histogram logdensity
        hist2 = histogram(df, bounds, ax3)
        ax3.xaxis.set_visible(False)

        # Fourth column
        # load rebinned calibrater data and plot it!
        data_path = condition['sensor'][rebinned]['data']
        df = load_data(data_path)

        # Get bins
        bounds = sensors[rebinned]['bins']

        # Pick an axes
        ax4 = plt.subplot(gs[i, 3])

        # Histogram logdensity
        hist3 = histogram(df, bounds, ax4)
        ax4.xaxis.set_visible(False)

        # First row
        if i == 0:
            ax2.set_title(sensors[calibratee]['name'])
            ax3.set_title(sensors[calibrater]['name'])
            ax4.set_title(sensors[rebinned]['name'])

        # Last row
        if i == (nrows-1):
            ax2.xaxis.set_ticks_position('bottom')
            ax2.xaxis.set_visible(True)
            ax3.xaxis.set_ticks_position('bottom')
            ax3.xaxis.set_visible(True)
            ax4.xaxis.set_ticks_position('bottom')
            ax4.xaxis.set_visible(True)

            # Third column
            ax3.set_xlabel(x_label)
            # ax.annotate(x_label, xy=(0.5, 0),
                        # xycoords=('axes fraction', 'axes fraction'),
                        # xytext=(0, 6),
                        # textcoords='offset points',
                        # ha='center', va='center')

        try:
            # Combine histogram stats
            exp_stats_dict[exp] = {sensors[calibratee]['name']: hist1,
                                   sensors[calibrater]['name']: hist2,
                                   sensors[rebinned]['name']: hist3}

        except:
            logging.exception('Got exception on main handler')
            raise

    kwargs = {"bbox_inches": "tight"}
    if 'plots' not in settings:
        settings['plots'] = {}
    settings['plots']['hist-mat'] = saveplot(output_file, fig, **kwargs)
    plt.close()

    table(exp_stats_dict)

    # Dump the json
    with open(settings_file, 'w') as handle:
        json.dump(settings, handle, default=date_handler,
                  sort_keys=True, indent=4)
