#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib
import json
import yaml
import argparse
from src.modules.data import *
from src.modules.analysis import *
from datetime import datetime, timedelta
from pint import UnitRegistry
import copy
import logging

logging.basicConfig(filename='log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


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

# Create some directories if they do not exist

# Base project directory
project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
project_dir = os.path.abspath(project_dir)

# Base imgs directory
base_imgs_dir = os.path.join(project_dir, "imgs", "calibration")
if not os.path.isdir(base_imgs_dir):
    os.makedirs(base_imgs_dir)

# Base interim data directory
base_interim_data_dir = os.path.join(project_dir, "data", "interim",
                                     "calibration")
if not os.path.isdir(base_interim_data_dir):
    os.makedirs(base_interim_data_dir)

# Base processed data directory
base_processed_data_dir = os.path.join(project_dir, "data", "processed",
                                     "calibration")
if not os.path.isdir(base_processed_data_dir):
    os.makedirs(base_processed_data_dir)


def loadSensorsData(sensors, sensorsFile, outputConc):
    # Load sensors definitions
    with open(sensorsFile) as handle:
        sensorDefinition = yaml.load(handle)

    # Initialise pint's UnitRegistry
    ureg = UnitRegistry()

    debug = ("Loading sensor data")
    logging.debug(debug)

    # Load data for a sensor
    for sensor in sensors:
        logging.debug("Sensor: %s" % (sensor))
        # Name the dataset
        sensorName = sensors[sensor]['name']
        # Get settings for this sensor
        settings = sensors[sensor]['sensor']
        # What type of sensor it is?
        type = settings['type']
        # Load definition into selected sensor
        settings.update(sensorDefinition[type])

        # Where is the data in data/raw/?
        sensor_dir = settings['path']
        data_dir = os.path.join(project_dir, "data", "raw", sensor_dir)

        # Fetch information about bin boundaries for this sensor
        bins = settings['bins']

        # Load data
        bins = loadData(data_dir, bins, sensorName)
        data = bins['data']

        # If the data is not in minute frequency, resample it
        if 'resample' in settings:
            if 'minute' == settings['resample']:
                data = data.resample('T', label='left', closed='left').mean()

        if 'realcounts' in settings:
            # Subtract high bins from lower
            data = realCounts(data)

        # How much time should the data produced by this sensor be shifted?
        # Shift datetime index of data
        if 'timeshift' in settings:
            timeshift = settings['timeshift']
            sign = timeshift[0]
            period = timeshift[1:]
            t = datetime.strptime(period, "%H:%M:%S")
            delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            debug = "Time shifted by %s %s" % (sign, str(delta))
            logging.debug(debug)
            debug = ("Before timeshift\n"
                     "Start: %s, end: %s" % (data.index[0], data.index[-1]))
            logging.debug(debug)
            if sign == '-':
                data.index = data.index - delta
            elif sign == '+':
                data.index = data.index + delta
            else:
                raise ValueError("Sign not given for timeshift")
            debug = ("After timeshift\n"
                     "Start: %s, end: %s" % (data.index[0], data.index[-1]))
            logging.debug(debug)

        # Scaling and unit conversion of particle concentration
        inputConc = settings['concentration']
        scale = float((ureg(outputConc))/(ureg(inputConc)))
        settings['scale factor'] = scale

        # Multiply the data with scale factor and update binDate dict
        bins['data'] = data*scale
        debug = "The scaling factor is %s" % (scale)
        logging.debug(debug)

        # Update settings dict with bins
        settings['bins'] = bins

        # Update sensor dict with settings
        sensors[sensor]['sensor'] = settings

    logging.debug("Rebinning calibrater")

    # Rebin calibrater data to calibratee bin boundaries
    calibratee = sensors['calibratee']['sensor']['bins']
    # Calibrater
    calibrater = sensors['calibrater']['sensor']['bins']

    # Bin boundaries of final set of bins
    finalBins = calibratee['bounds']

    # rebin calibrater dataset to match calibratee dataset
    rebinned = rebin(calibrater, finalBins)
    name = "rebinned-" + sensors['calibrater']['name']
    writeData(rebinned['data'], base_interim_data_dir, name)
    sensors['rebinned'] = {}
    sensors['rebinned']['name'] = name
    sensors['rebinned']['sensor'] = {}
    sensors['rebinned']['sensor']['bins'] = rebinned
    debug = ("Start: %s, end: %s" % (rebinned['data'].index[0],
                                     rebinned['data'].index[-1]))
    logging.debug(debug)
    return sensors


def experiments(expDict, sensors):
    # Experiments

    # # Load experiment information such as times of stimulus
    # with open(expFile) as handle:
        # configDict = yaml.load(handle)
    order = expDict['order']
    conditions = expDict['conditions']

    # Concat rebinned data with calibratee data
    calibraterData = sensors['rebinned']['sensor']['bins']['data']
    calibrateeData = sensors['calibratee']['sensor']['bins']['data']
    calibrationData = concat(calibrateeData, calibraterData)
    calibrated = calibrate(calibrationData)

    # Initialise a DataFrame to store mean particle counts of each experiment for
    # a calibratee and rebinned calibrater
    index = order
    columns = calibrated.columns
    calibration = pd.DataFrame(index=index, columns=columns)
    caliName = sensors['calibrater']['name'] + "-" + sensors['calibratee']['name']

    logging.debug("Experiment time")
    # Iterate over different experiment conditions
    for exp in order:
        condition = conditions[exp]

        imgs_dir = os.path.join(base_imgs_dir, exp)
        if not os.path.isdir(imgs_dir):
            os.makedirs(imgs_dir)
        interim_data_dir = os.path.join(base_interim_data_dir, exp)
        if not os.path.isdir(interim_data_dir):
            os.makedirs(interim_data_dir)
        processed_data_dir = os.path.join(base_processed_data_dir, exp)
        if not os.path.isdir(processed_data_dir):
            os.makedirs(processed_data_dir)

        # Load start and end datetime for time series data
        time = condition['time']
        start = time['start']
        end = time['end']

        condition['data'] = {}

        # Iterate over different sensors
        try:
            for sensor in sensors:
                    dataDict = {}
                    sensorDict = sensors[sensor]

                    # Name the processed data
                    sensorName = sensorDict['name']

                    # Load data from sensor dict from time period
                    # Copy the bins data into new dict
                    sample = copy.deepcopy(sensorDict['sensor']['bins'])
                    fullstart = sensorDict['sensor']['bins']['data'].index[0]
                    fullend = sensorDict['sensor']['bins']['data'].index[-1]
                    debug = ("Exp: %s, Sensor: %s,\n"
                             "Data start: %s and end: %s\n"
                             "Sample start: %s and end: %s\n" % (exp, sensor,
                                                               fullstart,
                                                               fullend, start, end))
                    logging.debug(debug)
                    sample['data'] = sample['data'].loc[start:end]

                    realstart = sample['data'].index[0]
                    realend = sample['data'].index[-1]
                    debug = ("Sample start: %s and end: %s\n" % (realstart, realend))
                    logging.debug(debug)

                    # Does data from this sensor need processing?
                    if 'process' in sensorDict:
                        # Check if any bins have zero counts and drop them
                        if 'prunebins' in sensorDict['process']:
                            # Prune bins from data that have zero counts
                            sample = pruneBins(sample)

                    # Write sample to file
                    writeData(sample['data'], interim_data_dir, sensorName)

                    # Plot selected time series data
                    plotPath = plot(sample['data'], imgs_dir, sensorName)
                    dataDict["plot"] = plotPath.replace("\\\\", "/")

                    # Plot histogram and get statistics
                    histDict = histogram(sample, imgs_dir, processed_data_dir, sensorName)
                    dataDict["histogram"] = histDict

                    # Add data collected so far for this experiment and sensor to main
                    # dictionary
                    condition['data'][sensor] = dataDict

            conditions[exp] = condition
            logging.debug("Calibrating")
            df = calibrationData.loc[start:end]
            dict = {}
            calibratee = sensors['calibratee']['sensor']['bins']['columns']
            calibrater = sensors['rebinned']['sensor']['bins']['columns']
            columns = calibrater + calibratee
            dict['plot'] = plot(df[columns], imgs_dir, caliName)

            # Calculate calibration factors
            mean = calibrated.loc[start:end].mean()
            calibration.loc[exp] = mean
            condition['data']['calibration'] = dict
            del sample

        except Exception as e:
            del conditions[exp]
            order.remove(exp)
            logging.exception(e)
            logging.debug(exp)
            continue

    # Add data collected for all experiments and write to file
    latex = save_latex(calibration, base_processed_data_dir, caliName, "calibration")
    expDict['calibration'] = latex
    expDict['conditions'] = conditions
    return expDict


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Settings yaml file")
    parser.add_argument("sensors", help="Sensors defintions yaml file")
    parser.add_argument("-o", "--output", help="Directs the output to a name of your choice")

    options = parser.parse_args()
    settingsFile = options.settings
    sensorsFile = options.sensors
    outputFile = options.output

    # Load settings yaml file
    with open(settingsFile) as handle:
        settings = yaml.load(handle)

    # Final particle concentration
    outputConc = settings['output']['concentration']

    # Sensors
    sensorsDict = settings['sensors']

    # Experimental conditions
    expDict = settings['exp']

    # Load information about sensors and load data for each sensor
    sensorsDict = loadSensorsData(sensorsDict, sensorsFile, outputConc)

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
