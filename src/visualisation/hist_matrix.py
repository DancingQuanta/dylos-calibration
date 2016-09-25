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
    # Bin boundaries
    lower = bounds[:-1]
    upper = bounds[1:]

    # Take a mean of the input dataframe to form a histogram
    counts = df.mean(axis=0).values
    y = counts / (np.log10(upper) - np.log10(lower))

    # Plot lognormal
    x1 = lower  # left edge
    x2 = upper  # right edge
    w = np.array(x2)-np.array(x1)  # variable width
    ax.bar(x1, y, width=w)
    ax.set_xscale('log')


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Date file")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")

    options = parser.parse_args()
    settings_file = options.settings
    output_file = options.output

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

    # Matrix dimension
    nrows=len(exp_order)
    ncols=len(sensor_order)

    # Fig size
    fig_width = 2.2
    fig_height = 1.6
    fig_size = [(fig_width * ncols), (fig_height * nrows)]
    params = {"figure.figsize": fig_size}
    matplotlib.rcParams.update(params)

    fig, axarr = plt.subplots(nrows=nrows, ncols=ncols)
    axes = fig.axes
    # fig.subplots_adjust(hspace=0.05, wspace=0.05)
    x_label = r'Diameter / \si{\um}'
    y_label = r'Frequency per $\log D$'

    k = 0
    plt.annotate(x_label, xy=(0.5, 0),
                xycoords=('figure fraction', 'figure fraction'),
                xytext=(0, 6),
                textcoords='offset points',
                ha='center', va='center')
    plt.annotate(y_label, xy=(0, 0.5),
                xycoords=('figure fraction', 'figure fraction'),
                xytext=(10, 0),
                textcoords='offset points',
                ha='center', va='center',
                rotation='vertical')
    for i, sensor in enumerate(sensor_order):
        for j, exp in enumerate(exp_order):
            condition = conditions[exp]
            # Get name
            sensor_name = 'test'
            x_title = sensors[sensor]['name']
            y_title = r"\SI{%s}{\um}" % (exp)

            # load data
            data_path = condition['sensor'][sensor]['data']
            df = load_data(data_path)

            # Get bins
            bounds = sensors[sensor]['bins']

            # Pick an axes
            ax = axarr[j,i]

            # Histogram logdensity
            histogram(df, bounds, ax)

            # Setting labels
            ax.xaxis.set_visible(False)
            if i == 0:
                ax.annotate(y_title, xy=(0, 0.5),
                            xycoords=('axes fraction', 'axes fraction'),
                            xytext=(-40, 0),
                            textcoords='offset points',
                            size=12, ha='center', va='bottom')

            if j == 0:
                ax.set_title(x_title)

            if j == nrows:
                ax.xaxis.set_ticks_position('bottom')
            k += 1

    kwargs = {"bbox_inches": "tight"}
    saveplot(output_file, fig, **kwargs)
    plt.close()
    # Dump the plot path to json
    settings['plots'] = {}
    settings['plots']['hist-mat'] = output_file
    dump = json.dumps(settings, default=date_handler,
                     sort_keys=True, indent=4).replace("\\\\", "/")
    with open(settings_file, 'w') as handle:
            handle.write(dump)

