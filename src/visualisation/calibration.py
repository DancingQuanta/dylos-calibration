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
    # ax.legend(loc='lower right')

    # ax.set_xlabel(x_label)
    # ax.set_ylabel(y_label)
    binsize = r"\SI{%s}{\um} Bin" % (bin)
    results_dict = {bin: {'slope': results[0],
                          'slope error': results[1],
                          'intercept': results[2],
                          'intercept error': results[3],
                          'rs': results[4]}}
    return binsize, results_dict


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


def regression_table(dict, order, path):
    """
    Generate a latex table out of regression analysis of each particle size
    """
    # Ensure absolute path
    path = os.path.abspath(path)

    bins = ['0.5', '2.5']
    first = (r'\begin{tabular}{ccccccc}' + '\n'
             r'\multirow{2}{*}{Particle size} & ' +
             r'\multicolumn{3}{c}{\SI{0.5}{\um}} & ' +
             r'\multicolumn{3}{c}{\SI{2.5}{\um}} \\' + '\n')
    labels = ['Slope', 'Intercept', 'R-Squared']
    second = ('& ' + ' & '.join(labels) + ' & ' +
              ' & '.join(labels) + ' \\\\ \n \\toprule\n')

    line = []
    lines = []
    # loop over particle sizes and bins
    for x in order:
        line += [x]
        for y in bins:
            a = dict[x][y]
            slope = '$%.3f \\pm %.3f$' % (a['slope'], a['slope error'])
            intercept = '$%.3f \\pm %.3f$' % (a['intercept'], a['intercept error'])
            rs = '%.3f' % a['rs']
            line += [slope, intercept, rs]
        lines += ' & '.join(line) + ' \\\\ \n'
        line = []

    # Join parts of table together
    table = first + second + ''.join(lines) + '\\bottomrule \n\\end{tabular}'

    with open(path, 'w') as f:
        f.write(table)
    return path.replace("\\", "/")


if __name__ == '__main__':
    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Date file")
    parser.add_argument("-p", "--plot",
                        help="Path to plot")
    parser.add_argument("-s", "--stats",
                        help="Path to statistics")

    options = parser.parse_args()
    settings_file = options.settings
    plot_path = options.plot
    stats_path = options.stats

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

    # Experimental conditions
    exps = settings['exp']

    # Conditions
    exp_order = exps['order']
    conditions = exps['conditions']

    # Matrix dimension
    nrows = len(exp_order)
    ncols = 2

    # Fig size
    fig_width = 2.8
    golden_mean = (np.sqrt(5.0)-1.0) / 2.0
    fig_height = fig_width * golden_mean
    width_ratios = [0.5] + ncols * [1]
    fig_size = [(fig_width * sum(width_ratios)), (fig_height * nrows)]

    # Create matrix with first columns for particles
    fig = plt.figure(figsize=fig_size)
    gs = gridspec.GridSpec(nrows, (ncols + 1),
                           width_ratios=width_ratios,
                           wspace=0.5, hspace=0.3)

    # First column
    ax = plt.subplot(gs[0, 0])
    ax.set_title(exps['parameter'])
    ax.annotate(y_label, xy=(1, 0.5),
                xycoords=('axes fraction', 'figure fraction'),
                xytext=(5, 10),
                textcoords='offset points',
                ha='center', va='center',
                rotation='vertical')

    reg_dict = {}
    stats = {}
    for i, exp in enumerate(exp_order):
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
        binsize1, reg_dict1 = calibrate(x, y, x_label, y_label, ax2)

        # Second column
        x = calibratee_data[calibratee_data.columns[1]]
        y = rebinned_data[rebinned_data.columns[1]]

        # Pick an axes
        ax3 = plt.subplot(gs[i, 2])

        # Calibrate and plot scatter
        binsize2, reg_dict2 = calibrate(x, y, x_label, y_label, ax3)

        # First row
        if i == 0:
            ax2.set_title(binsize1)
            ax3.set_title(binsize2)

        stats[exp] = {**reg_dict1, **reg_dict2}


    # Taking axes from last row
    # x label
    ax3.annotate(x_label, xy=(0, 0),
                 xycoords=('axes fraction', 'axes fraction'),
                 xytext=(-20, -22),
                 textcoords='offset points',
                 ha='center', va='center')

    kwargs = {"bbox_inches": "tight"}
    if 'plots' not in settings:
        settings['plots'] = {}
    settings['plots']['cali-mat'] = saveplot(plot_path, fig, **kwargs)
    plt.close()

    # Write regression results to file
    if 'stats' not in settings:
        settings['stats'] = {}
    settings['stats']['cali'] = regression_table(stats, exp_order, stats_path)

    # Dump the json
    with open(settings_file, 'w') as handle:
        json.dump(settings, handle, default=date_handler,
                  sort_keys=True, indent=4)
