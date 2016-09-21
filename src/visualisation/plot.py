#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import argparse
from utils import *

def index_mins(df):
    period = (df.index - df.index[0]).astype('timedelta64')
    mins = period.total_seconds() / 60
    df.index = mins
    return df


def plot(df, path):
    # Change the index of df to minutes
    df = index_mins(df)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    df.plot(ax=ax)
    plt.ylabel('Particle count')
    plt.xlabel('Time/min')

    lines, labels = ax.get_legend_handles_labels()
    # ax.legend(lines, labels, loc='upper center', mode='expand')
    art = []
    lgd = ax.legend(lines, labels, loc=9, bbox_to_anchor=(0.5, -0.2), ncol=2)
    art.append(lgd)
    kwargs = {"additional_artists": art,
              "bbox_inches": "tight"}

    path = saveplot(path, fig, **kwargs)
    plt.close()


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("data", help="Date file")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")
    parser.add_argument("-f", "--figsize",
                        help="Figure size")

    options = parser.parse_args()
    data_path = options.data
    output_file = options.output
    fig_size = options.figsize

    # Set figure size
    if fig_size is not None:
        params = {"figure.figsize": figsize(float(fig_size))}
    else:
        params = {"figure.figsize": figsize(0.49)}
    matplotlib.rcParams.update(params)

    # load data
    df = load_data(data_path)

    # Plot data
    plot(df, output_file)
