#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib
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
    # Initialise new series
    columns = ['Counts', "dN/logD"]
    df1 = pd.DataFrame(columns=columns)

    # Take a mean of the input dataframe which becomes a series with column
    df1['Counts'] = df.mean(axis=0)
    df1["dN/logD"] = df1["Counts"] / np.log10(bounds[1:]) - np.log10(bounds[:-1])

    # Plot lognormal
    x1 = bounds[:-1]  # left edge
    x2 = bounds[1:]  # right edge
    w = np.array(x2)-np.array(x1)  # variable width
    y = df1["dN/logD"].tolist()
    ax.bar(x1, y, width=w)
    ax.set_xscale('log')


def set_ax(ax, x_title, y_title):
    ax.xaxis.set_visible(False)
    if ax.is_first_col():
        ax.annotate(y_title, xy=(0, 0.5),
                    xycoords=('axes fraction', 'axes fraction'),
                    xytext=(10, 0),
                    textcoords='offset points',
                    size=14, ha='center', va='bottom')
    # if ax.is_last_col():

    if ax.is_first_row():
        ax.set_title(x_title)
    if ax.is_last_row():
        ax.xaxis.set_ticks_position('bottom')


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Date file")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")
    parser.add_argument("-f", "--figsize",
                        help="Figure size")

    options = parser.parse_args()
    settings_file = options.settings
    output_file = options.output
    fig_size = options.figsize

    # Set figure size
    if fig_size is not None:
        params = {"figure.figsize": figsize(float(fig_size))}
    else:
        params = {"figure.figsize": figsize(0.49)}
    matplotlib.rcParams.update(params)

    # Load settings yaml file
    with open(settings_file) as handle:
        settings = json.load(handle)

    # Sensors
    sensors = settings['sensors']
    sensor_order = settings['sensor_order']

    # Experimental conditions
    exps = settings['exp']

    # Conditions
    exp_order = exps['order']
    conditions = exps['conditions']

    fig, axarr = plt.subplots(nrows=len(exp_order), ncols=len(sensor_order))
    axes = fig.axes
    fig.subplots_adjust(hspace=0.05, wspace=0.05)
    k = 0
    for exp in exp_order:
        condition = conditions[exp]
        for sensor in sensor_order:
            # Get name
            sensor_name = sensors[sensor]['name']
            condition_name = condition

            # load data
            data_path = condition['sensor'][sensor]['data']
            df = load_data(data_path)

            # Get bins
            bounds = sensors[sensor]['bins']

            # Pick an axes
            ax = axes[k]

            # Histogram logdensity
            histogram(df, bounds, ax)

            # Plot
            set_ax(ax, sensor_name, condition_name)
            k += 1

    x_label = r'$\mathbf{Diameter}$ / $\mu$'
    y_label = r'Frequency per $\log D$'
    fig.text(0.5, 0.04, x_label, ha='center', va='center')
    fig.text(0.06, 0.5, y_label, ha='center', va='center', rotation='vertical')
    saveplot(output_file, fig)
    plt.close()
