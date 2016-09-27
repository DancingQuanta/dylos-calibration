#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
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

def plot(df, ax):
    # Change the index of df to minutes
    df = index_mins(df)

    # Plot timeseries
    df.plot(ax=ax, legend=False)


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
    ncols=2

    # Fig size
    fig_width = 3
    fig_height = 1.6
    fig_size = [(fig_width * ncols), (fig_height * nrows)]

    # Create matrix with first columns for particles
    fig = plt.figure(figsize=fig_size)
    width_ratios = [1] + ncols * [2]
    gs = gridspec.GridSpec(nrows, (ncols + 1),
                           width_ratios=width_ratios)
                           # wspace=0.5, hspace=0.10)

    x_label = r'Time / min'
    y_label = r'Particle counts'

    # First column
    ax = plt.subplot(gs[0, 0])
    ax.set_title("Particle size")
    ax.annotate(y_label, xy=(1, 0.5),
                xycoords=('axes fraction', 'figure fraction'),
                xytext=(10, 0),
                textcoords='offset points',
                ha='center', va='center',
                rotation='vertical')

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

        # Second column
        # load calibrater data and plot it!
        data_path = condition['sensor'][calibrater]['data']
        df = load_data(data_path)

        # Pick an axes
        ax2 = plt.subplot(gs[i, 1])

        # Plot timeseries
        plot(df, ax2)

        # Third column
        # load calibratee and rebinned data and plot it!
        data_path = condition['sensor'][calibratee]['data']
        df = load_data(data_path)

        data_path = condition['sensor'][rebinned]['data']
        df1 = load_data(data_path)
        df = concat(df,df1)

        # Pick an axes
        ax3 = plt.subplot(gs[i, 2])

        # Plot timeseries
        plot(df, ax3)

    fig.text(2/3, 0.00, x_label, ha='center', va='center')

    kwargs = {"bbox_inches": "tight"}
    settings['plots'] = {}
    settings['plots']['plot-mat'] = saveplot(output_file, fig, **kwargs)
    plt.close()
    # Dump the plot path to json
    dump = json.dumps(settings, default=date_handler,
                     sort_keys=True, indent=4).replace("\\\\", "/")
    with open(settings_file, 'w') as handle:
            handle.write(dump)


#     lines, labels = ax.get_legend_handles_labels()
    # # ax.legend(lines, labels, loc='upper center', mode='expand')
    # art = []
    # lgd = ax.legend(lines, labels, loc=9, bbox_to_anchor=(0.5, -0.2), ncol=2)
    # art.append(lgd)
    # kwargs = {"additional_artists": art,
              # "bbox_inches": "tight"}

    # path = saveplot(path, fig, **kwargs)

