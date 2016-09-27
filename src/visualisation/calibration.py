#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import matplotlib.pyplot as plt
from matplotlib import gridspec
import pandas as pd
from scipy import polyval
import statsmodels.api as sm
from utils import *


def load_data(path):
    """Load a dataset
    """
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col=0,
                     infer_datetime_format=True)
    return df


def calibrate(x, y, x_label, y_label, ax):
    # What bin is it?
    sensor, bin = x.name.split('-')

    # Label lines
    label = r"\SI{%s}{\um}" % (bin)
    fit_label = r"Best fit " + label

    ax.scatter(x, y, label=label)

    # Regression analysis
    results = regression(x, y)
    slope = results[0]
    intercept = results[2]

    # Create best fit line
    yf = polyval([slope, intercept], x)
    ax.plot(x, yf, label=fit_label)
    ax.legend(loc='lower right')

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)


def regression(x, y):
    # Add a column of 1s to ensure intercept can be calculated
    # by regression analysis of statsmodel
    x = sm.add_constant(x, prepend=False)
    # Linear regression
    result = sm.OLS(y, x).fit()
    slope, intercept = result.params
    slopeerr, intercepterr = result.bse
    rs = result.rsquared
    results = (slope, slopeerr, intercept, intercepterr, rs)
    return results


if __name__ == '__main__':
    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Date file")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")

    options = parser.parse_args()
    settings_file = options.settings
    output_file = options.output

    # Load settings json file
    with open(settings_file) as handle:
        settings = json.load(handle)

    # Load info
    calibratee = settings['calibration']['calibratee']
    rebinned = settings['calibration']['rebinned']
    sensors = settings['sensors']

    # Axes labels
    x_label = sensors[calibratee]['name']
    y_label = sensors[rebinned]['name']

    # Conditions
    exp_order = settings['exp']['order']
    conditions = settings['exp']['conditions']

    # Matrix dimension
    nrows = len(exp_order)
    ncols = 2

    # Fig size
    fig_width = 2.5
    fig_height = fig_width*0.8
    width_ratios = [0.5] + ncols * [1]
    fig_size = [(fig_width * sum(width_ratios)), (fig_height * nrows)]

    # Create matrix with first columns for particles
    fig = plt.figure(figsize=fig_size)
    gs = gridspec.GridSpec(nrows, (ncols + 1),
                           width_ratios=width_ratios)

    # First column
    ax = plt.subplot(gs[0, 0])
    ax.set_title("Particle size")

    for i, exp in enumerate(exp_order):
        condition = conditions[exp]
        # Get name
        y_title = r"\SI{%s}{\um}" % (exp)

        # First column
        ax1 = plt.subplot(gs[i, 0])
        ax1.annotate(y_title, xy=(0.5, 0.5),
                     xycoords=('axes fraction', 'axes fraction'),
                     xytext=(0, 0),
                     textcoords='offset points',
                     size=11, ha='center', va='bottom')
        ax1.axis('off')

        # Load data path
        calibratee_path = condition['sensor'][calibratee]['data']
        rebinned_path = condition['sensor'][rebinned]['data']

        # Load data
        calibratee_data = load_data(calibratee_path)
        rebinned_data = load_data(rebinned_path)

        # First column
        x = calibratee_data[calibratee_data.columns[0]]
        y = rebinned_data[rebinned_data.columns[0]]

        # Pick an axes
        ax2 = plt.subplot(gs[i, 1])

        # Calibrate and plot scatter
        calibrate(x, y, x_label, y_label, ax2)

        # Second column
        x = calibratee_data[calibratee_data.columns[1]]
        y = rebinned_data[rebinned_data.columns[1]]

        # Pick an axes
        ax3 = plt.subplot(gs[i, 2])

        # Calibrate and plot scatter
        calibrate(x, y, x_label, y_label, ax3)


    kwargs = {"bbox_inches": "tight"}
    settings['plots'] = {}
    settings['plots']['cali-mat'] = saveplot(output_file, fig, **kwargs)
    plt.close()
    # Dump the plot path to json
    dump = json.dumps(settings, default=date_handler,
                      sort_keys=True, indent=4).replace("\\\\", "/")
    with open(settings_file, 'w') as handle:
            handle.write(dump)
