#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib


# matplotlib settings
params = {                      # setup matplotlib to use latex for output
    "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
    "text.latex.unicode": False,
    # "text.usetex": True,                # use LaTeX to write all text
    "font.family": "serif",
    "font.serif": [],                   # blank entries should cause plots to inherit fonts from the document
    "font.sans-serif": [],
    "font.monospace": [],
    "axes.labelsize": 10,               # LaTeX default is 10pt font.
    'font.size': 10,
    "legend.fontsize": 8,               # Make the legend/label fonts a little smaller
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "pgf.preamble": [
        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)
        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble
        r"\usepackage{amsmath}",
        r"\usepackage{siunitx}"
        ]
    }
matplotlib.rcParams.update(params)


def figsize(scale):
    fig_width_pt = 483.69687                          # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0 / 72.27                       # Convert pt to inch
    golden_mean = (np.sqrt(5.0)-1.0) / 2.0            # Aesthetic ratio (you could change this)
    fig_width = fig_width_pt * inches_per_pt*scale    # width in inches
    fig_height = fig_width * 0.80              # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size


def load_data(path):
    """Load a dataset
    """
    df = pd.read_csv(path,
                     parse_dates=[0],
                     infer_datetime_format=True)
    return df


def saveplot(path, fig, **kwargs):
    print("Plotting: %s" % (path))
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[-1]
    name = os.path.splitext(filename)[0]
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    if ext is not ".pgf":
        # Save plot in original extension without kwargs
        fig.savefig(path)
        # Then save plot as pgf
        filename = name + ".pgf"
        path = os.path.join(dir, filename)
        fig.savefig(path, **kwargs)
    else:
        fig.savefig(path, **kwargs)


def save_latex(df, path, kind, **kwargs):
    """Save a DataFrame to latex table via to_latex()

    Args:
        df: Pandas.DataFrame
        path: str
            where outputfile will be saved to
        kwargs: **
            pass keywords unto pd.to_latex()
    Returns:
        path: str
            location and filename of saved latex file which can used to input
            into a latex document with \input(path)

    """
    filename = os.path.basename(path)
    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[-1]
    filename = name + "-" + kind + ".tex"
    dir = os.path.dirname(path)
    path = os.path.join(dir, filename)

    latex = df.to_latex(**kwargs)
    with open(path, 'w') as f:
        f.write(latex)


def nmoment(x, counts, c, n):
    return np.sum(((x-c)**n)*counts) / np.sum(counts)


def statistics(midpoints, counts):
    """Statistics for binned data

    Args:
        counts: ndarray
        midpoints: adarray

    Returns:

    """
    # Mean
    mean = nmoment(midpoints, counts, 0, 1)

    # Standard deviation
    std = nmoment(midpoints, counts, mean, 2)**0.5

    # Lower 95% bounds
    lower = mean - 2 * std

    # Upper 95% bounds
    upper = mean + 2 * std

    return mean, std, lower, upper
