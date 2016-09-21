#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
import pandas as pd
import argparse

# # matplotlib settings
# params = {
# "figure.figsize": figsize(0.49),     # fig size for latex
# }
# matplotlib.rcParams.update(params)


def load_data(path):
    """Load a dataset
    """
    df = pd.read_csv(path,
                     parse_dates=[0],
                     index_col='Datetime',
                     infer_datetime_format=True)
    return df


def index_mins(df):
    period = df.index - df.index[0]
    mins = period.total_seconds() / 60
    df.index = mins
    return df


def saveplot(path, fig, **kwargs):
    print("Plotting: %s" % (path))
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[-1]
    if ext is not ".pgf":
        # Save plot in original extension without kwargs
        fig.savefig(path)
        # Then save plot as pgf
        name = os.path.splitext(filename)[0]
        filename = name + ".pgf"
        dir = os.path.dirname(path)
        path = os.path.join(dir, filename)
        fig.savefig(path, **kwargs)
    else:
        fig.savefig(path, **kwargs)


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

    options = parser.parse_args()
    data_path = options.data
    output_file = options.output

    # load data
    df = load_data(data_path)

    # Plot data
    plot(df)
