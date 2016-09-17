#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compare two dylos sensors DC1700 and DC1100 Pro
"""

import os
import json
import yaml
import argparse
import matplotlib
from matplotlib import pyplot as plt
import pandas as pd
from src.modules.data import realCounts, date_handler
from src.modules.analysis import twoplot, figsize
import logging

logging.basicConfig(filename='log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.WARNING)


# matplotlib.style.use('ggplot')
pd.options.display.float_format = '{:.2f}'.format

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
    "figure.figsize": figsize(0.49),     # default fig size of 0.9 textwidth
    "pgf.preamble": [
        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)
        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble
        ]
    }
matplotlib.rcParams.update(params)

def loadData(path, columns):
    if os.path.exists(path):
        cols = ['Datetime'] + columns
        df = pd.read_csv(path,
                         parse_dates=[0],
                         index_col='Datetime',
                         infer_datetime_format=True,
                         header=None,
                         names=cols
                        )
        return df
    else:
        raise ValueError(path + " does not exists")


def loadSensorsData(sensors):
    debug = ("Loading sensor data")
    logging.debug(debug)

    # Load config for a sensor
    dylos2 = sensors['dylos2']

    # Dylos DC1700
    dylos1 = sensors['dylos1']
    path = os.path.join(data_dir, dylos1['path'])
    columns = ['0.5-Dylos1', '2.5-Dylos1']
    dylos1['data'] = loadData(path, columns)
    dylos1['data'].index = dylos1['data'].index.values.astype('<M8[m]')
    dylos1['data'] = realCounts(dylos1['data'])
    sensors['dylos1'] = dylos1

    # Dylos DC1100 Pro
    dylos2 = sensors['dylos2']
    path = os.path.join(data_dir, dylos2['path'])
    columns = ['0.5-Dylos2', '2.5-Dylos2']
    dylos2['data'] = loadData(path, columns)
    dylos2['data'].index = dylos2['data'].index.values.astype('<M8[m]')
    dylos2['data'] = realCounts(dylos2['data'])
    sensors['dylos2'] = dylos2
    return sensors


def experiments(expDict, sensors):
    # Experiments

    # # Load experiment information such as times of stimulus
    order = expDict['order']
    conditions = expDict['conditions']

    logging.debug("Experiment time")
    # Iterate over different experiment conditions
    for exp in order:
        condition = conditions[exp]
        dict = {}
        imgs_dir = os.path.join(base_imgs_dir, exp)
        if not os.path.isdir(imgs_dir):
            os.makedirs(imgs_dir)
        # Load start and end datetime for time series data
        start = condition['start']
        end = condition['end']

        dylos1 = sensors['dylos1']['data'].loc[start:end]
        dylos2 = sensors['dylos2']['data'].loc[start:end]

        plotPath = twoplot(dylos1, dylos2, imgs_dir, "dylos")
        dict["twoplot"] = plotPath.replace("\\\\", "/")

        condition['results'] = dict
        conditions[exp] = condition

    # Add data collected for all experiments and write to file
    expDict['conditions'] = conditions
    return expDict


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Settings yaml file")
    parser.add_argument("-o", "--output", help="Directs the output to a name of your choice")

    options = parser.parse_args()
    settingsFile = options.settings
    outputFile = options.output

    name = os.path.basename(settingsFile)
    name = os.path.splitext(name)[0]

    # Base project directory
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    project_dir = os.path.abspath(project_dir)

    # Where is raw data?
    data_dir = os.path.join(project_dir, "data", "raw")

    # Create some directories if they do not exist

    # Base imgs directory
    base_imgs_dir = os.path.join(project_dir, "imgs", name)
    if not os.path.isdir(base_imgs_dir):
        os.makedirs(base_imgs_dir)

    # Load settings yaml file
    with open(settingsFile) as handle:
        settings = yaml.load(handle)

    # Sensors
    sensorsDict = settings['sensors']

    # Experimental conditions
    expDict = settings['exp']

    # Load information about sensors and load data for each sensor
    sensorsDict = loadSensorsData(sensorsDict)

    # Perform analysis on each experiment
    expDict = experiments(expDict, sensorsDict)

    # Output processed data
    settings['sensors'] = sensorsDict
    settings['exp'] = expDict
    outputDict = settings
    path = os.path.dirname(outputFile)
    if not os.path.isdir(path):
        os.makedirs(path)
    dump = json.dumps(outputDict, default=date_handler,
                      sort_keys=True, indent=4).replace("\\\\", "/")
    with open(outputFile, 'w') as outfile:
                outfile.write(dump)
