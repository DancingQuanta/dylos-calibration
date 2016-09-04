#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from src.modules.tools import *
from datetime import datetime, timedelta
import json
import yaml
import argparse
from pint import UnitRegistry
matplotlib.style.use('ggplot')
pd.options.display.float_format = '{:.2f}'.format

# matplotlib settings
params = {'backend': 'pdf',
          'axes.labelsize': 10,
          'axes.titlesize': 8,
          'font.size': 8,
          'legend.fontsize': 8,
          'xtick.labelsize': 8,
          'ytick.labelsize': 8,
          # 'text.usetex': True,
          'figure.figsize': [4.2, 3]
         }
matplotlib.rcParams.update(params)


def loadSensorsData(project_dir, sensors, sensorsFile, outputConc):
    # Load sensors definitions
    with open(sensorsFile) as handle:
        sensorDefinition = yaml.load(handle)

    # Initialise pint's UnitRegistry
    ureg = UnitRegistry()

    # Load data for a sensor
    for sensor in sensors:
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
            if sign == '-':
                data.index = data.index - delta
            elif sign == '+':
                data.index = data.index + delta

        # Scaling and unit conversion of particle concentration
        inputConc = settings['concentration']
        scale = float((ureg(outputConc))/(ureg(inputConc)))
        print(scale)

        # Multiply the data with scale factor and update binDate dict
        bins['data'] = data*scale

        # Update settings dict with bins
        settings['bins'] = bins

        # Update sensor dict with settings
        sensors[sensor]['sensor'] = settings

    # Rebin calibrater data to calibratee bin boundaries
    calibratee = sensors['calibratee']['sensor']['bins']
    # Calibrater
    calibrater = sensors['calibrater']['sensor']['bins']

    # Bin boundaries of final set of bins
    finalBins = calibratee['bounds']

    # rebin calibrater dataset to match calibratee dataset
    rebinned = rebin(calibrater, finalBins)
    name = "rebinned-" + sensors['calibrater']['name']
    sensors['rebinned'] = {}
    sensors['rebinned']['name'] = name
    sensors['rebinned']['sensor'] = {}
    sensors['rebinned']['sensor']['bins'] = rebinned
    return sensors


def experiments(project_dir, expDict, sensors):
    # Experiments

    # Create some directories if they do not exist
    base_imgs_dir = os.path.join(project_dir, "imgs", "calibration")
    if not os.path.isdir(base_imgs_dir):
        os.makedirs(base_imgs_dir)
    base_interim_data_dir = os.path.join(project_dir, "data", "interim",
                                         "calibration")
    if not os.path.isdir(base_interim_data_dir):
        os.makedirs(base_interim_data_dir)

    # # Load experiment information such as times of stimulus
    # with open(expFile) as handle:
        # configDict = yaml.load(handle)
    order = expDict['order']
    conditions = expDict['conditions']


    # Concat rebinned data with calibratee data
    calibraterData = sensors['rebinned']['sensor']['bins']['data']
    calibrateeData = sensors['calibratee']['sensor']['bins']['data']
    calibrationData = concat(calibraterData, calibrateeData)

    # Initize a DataFrame to store mean particle counts of each experiment for
    # a calibratee and rebinned calibrater
    index = order
    columns = calibrationData.columns
    calibration = pd.DataFrame(index=index, columns=columns)

    # Iterate over different experiment conditions
    for exp in order:
        print(exp)
        condition = conditions[exp]

        imgs_dir = os.path.join(base_imgs_dir, exp)
        if not os.path.isdir(imgs_dir):
            os.makedirs(imgs_dir)
        interim_data_dir = os.path.join(base_interim_data_dir, exp)
        if not os.path.isdir(interim_data_dir):
            os.makedirs(interim_data_dir)

        # Load start and end datetime for time series data
        time = condition['time']
        start = time['start']
        end = time['end']

        condition['data'] = {}

        # Iterate over different sensors
        for sensor in sensors:
            print(sensor)
            dataDict = {}
            sensorDict = sensors[sensor]

            # Name the processed data
            sensorName = sensorDict['name']

            # Load data from sensor dict from time period
            sample = sensorDict['sensor']['bins']
            sample['data'] = sample['data'].loc[start:end]

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
            histDict = histogram(sample, imgs_dir, sensorName)
            dataDict["histogram"] = histDict

            # Add data collected so far for this experiment and sensor to main
            # dictionary
            condition['data'][sensor] = dataDict

        df = calibrationData.loc[start:end]
        name = sensors['calibrater']['name'] + sensors['calibratee']['name']
        plotPath = plot(df, imgs_dir, name)
        dict = {}
        dict['plot'] = plotPath.replace("\\\\", "/")

        # Calculate calibration factors
        calibrated = calibrate(df)
        calibration.loc[exp] = calibrated
        dict['data'] = calibration

        condition['data']['calibration'] = dict
        conditions[exp] = condition

    # Add data collected for all experiments and write to file
    print(calibration)
    expDict['calibration'] = calibration.to_latex()
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

    # Base project directory
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    project_dir = os.path.abspath(project_dir)

    # Where should processed data go?
    processed_data_dir = os.path.join(project_dir, "data", "processed")
    if not os.path.isdir(processed_data_dir):
        os.makedirs(processed_data_dir)

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
    sensorsDict = loadSensorsData(project_dir, sensorsDict,
                                  sensorsFile, outputConc)

    # Perform analysis on each experiment
    expDict = experiments(project_dir, expDict, sensorsDict)

    # Output processed data
    settings['sensors'] = sensorsDict
    settings['exp'] = expDict
    outputDict = settings
    path = os.path.dirname(outputFile)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(outputFile, 'w') as outfile:
        json.dump(outputDict, outfile, default=date_handler,
                  sort_keys=True, indent=4)
