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


def loadSensorsData(sensors, sensorsFile, outputUnit):
    # Load sensors definitions
    with open(sensorsFile) as handle:
        sensorDefinition = yaml.load(handle)

    debug = ("Loading sensor data")
    logging.debug(debug)

    # Load data for a sensor
    for sensor in sensors:
        logging.debug("Sensor: %s" % (sensor))
        # Load config for a sensor
        config = sensors[sensor]

        # Name the dataset
        sensorName = config['id']

        # What type of sensor it is?
        type = config['type']

        # Load sensor definition
        config.update(sensorDefinition[type])

        # Where is the data in data/raw/?
        sensor_dir = config['path']
        data_dir = os.path.join(project_dir, "data", "raw", sensor_dir)

        # Fetch information about bin boundaries for this sensor
        bins = config['bins']

        # Load data
        bins = loadData(data_dir, bins, sensorName)
        data = bins['data']

        # If the data is not in minute frequency, resample it
        if 'resample' in config:
            if 'minute' == config['resample']:
                data = data.resample('T', label='left', closed='left').mean()

        if 'realcounts' in config:
            # Subtract high bins from lower
            data = realCounts(data)

        # How much time should the data produced by this sensor be shifted?
        # Shift datetime index of data
        if 'timeshift' in config:
            timeshift = config['timeshift']
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

        # Set seconds to zero
        data.index = data.index.values.astype('<M8[m]')

        # Units of data
        # Scaling and unit conversion of particle concentration
        # What is the unit of recorded measurements?
        inputUnit = ureg(config['unit'])
        if "flowrate" in config:
            inputFlowrate = ureg(config['flowrate'])

        # Create test quantities to compare dimensionality against
        counts_test = ureg("counts")
        vol_test = ureg("m ** 3")
        conc_test = counts_test / vol_test
        time_test = ureg("s")
        rate_test = counts_test / time_test
        flowrate_test = vol_test * rate_test


        # Compare dimensionality of input data and output unit
        # If output unit is concentration
        if outputUnit.dimensionality == conc_test.dimensionality:

            # If input unit is concentration
            if inputUnit.dimensionality == conc_test.dimensionality:
                scale = inputUnit.to(outputUnit).magnitude
                # scale = 1/float(outputUnit / inputUnit)
                if 'concentration' not in config:
                    config['concentration'] = str('{:.03f~}'.format(inputUnit))
                # Calculate count rate if not exists
                if 'count rate' not in config:
                    countrate = (inputFlowrate * inputUnit).to('counts per second')
                    config['count rate'] = str('{:.03f~}'.format(countrate))

            # If input unit is count rate
            elif inputUnit.dimensionality == rate_test.dimensionality:
                conc = inputUnit / inputFlowrate
                scale = float(outputUnit / conc)
                if 'count rate' not in config:
                    config['count rate'] = str('{:.03f}'.format(inputUnit))
                if 'concentration' not in config:
                    config['concentration'] = str('{:.03f}'.format(conc))

            else:
                msg = "The input unit is incorrect or not yet implementated!"
                raise ValueError(msg)
        else:
            msg = "The output unit is incorrect or not yet implementated!"
            raise ValueError(msg)

        config['scale factor'] = scale

        # Multiply the data with scale factor and update binDate dict
        bins['data'] = data*scale
        debug = "The scaling factor is %s" % (scale)
        logging.debug(debug)

        # Update settings dict with bins
        config['bins'] = bins

        # Write the results to disk
        writeData(bins['data'], base_interim_data_dir, sensorName)

        # Update sensor dict with settings
        sensors[sensor] = config

    logging.debug("Rebinning calibrater")

    # Rebin calibrater data to calibratee bin boundaries
    calibratee = sensors['calibratee']['bins']
    # Calibrater
    calibrater = sensors['calibrater']['bins']

    # Bin boundaries of final set of bins
    finalBins = calibratee['bounds']

    # rebin calibrater dataset to match calibratee dataset
    rebinned = rebin(calibrater, finalBins)
    name = "rebinned-" + sensors['calibrater']['id']
    writeData(rebinned['data'], base_interim_data_dir, name)
    debug = ("Start: %s, end: %s" % (rebinned['data'].index[0],
                                     rebinned['data'].index[-1]))
    logging.debug(debug)
    sensors['rebinned'] = {'id': name, 'bins': rebinned}
    return sensors


def experiments(expDict, sensors):
    # Experiments

    order = expDict['order']
    conditions = expDict['conditions']

    # Concat rebinned data with calibratee data and print to file
    caliName = sensors['calibrater']['id'] + "-" + sensors['calibratee']['id']
    calibraterData = sensors['rebinned']['bins']['data']
    calibrateeData = sensors['calibratee']['bins']['data']
    calibrationData = concat(calibrateeData, calibraterData)
    writeData(calibrationData, base_interim_data_dir, caliName)

    logging.debug("Experiment time")
    # Iterate over different experiment conditions
    reg_dict = {}
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
        start = condition['start']
        end = condition['end']

        condition['results'] = {}

        # Iterate over different sensors
        for sensor in sensors:
            dataDict = {}
            sensorDict = sensors[sensor]

            # Name the processed data
            sensorName = sensorDict['id']

            # Load data from sensor dict from time period
            # Copy the bins data into new dict
            sample = copy.deepcopy(sensorDict['bins'])
            fullstart = sensorDict['bins']['data'].index[0]
            fullend = sensorDict['bins']['data'].index[-1]
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
            # Check if any bins have zero counts and drop them
            if 'prunebins' in sensorDict:
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
            condition['results'][sensor] = dataDict

        conditions[exp] = condition

        # Calibration
        logging.debug("Calibrating")
        dict = {}
        df = calibrationData.loc[start:end]

        # Plot both rebinned calibrater and calibratee
        dict['plot'] = plot(df, imgs_dir, caliName)

        # Take a mean and ste
        paths, stats = calibrate(df, imgs_dir, processed_data_dir, name)

        reg_dict[exp] = stats
        dict['regression'] = paths

        condition['results']['calibration'] = dict
        del sample

    # Add data collected for all experiments and write to file
    latex = regression_table(reg_dict, order, base_processed_data_dir, caliName)
    expDict['calibration'] = latex
    expDict['conditions'] = conditions
    return expDict


if __name__ == '__main__':

    # Get filenames to work with
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("settings", help="Settings yaml file")
    parser.add_argument("sensors", help="Sensors defintions yaml file")
    parser.add_argument("-o", "--output",
                        help="Directs the output to a name of your choice")
    parser.add_argument("-f", "--figsize", help="Figure size")

    options = parser.parse_args()
    settingsFile = options.settings
    sensorsFile = options.sensors
    outputFile = options.output
    fig_size = options.figsize

    # Set figure size
    if fig_size is not None:
        params = {"figure.figsize": figsize(fig_size)}
    else:
        params = {"figure.figsize": figsize(0.49)}
    matplotlib.rcParams.update(params)

    name = os.path.basename(settingsFile)
    name = os.path.splitext(name)[0]

    # Base project directory
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    project_dir = os.path.abspath(project_dir)

    # Create some directories if they do not exist

    # Base imgs directory
    base_imgs_dir = os.path.join(project_dir, "imgs", name)
    if not os.path.isdir(base_imgs_dir):
        os.makedirs(base_imgs_dir)

    # Base interim data directory
    base_interim_data_dir = os.path.join(project_dir, "data", "interim", name)
    if not os.path.isdir(base_interim_data_dir):
        os.makedirs(base_interim_data_dir)

    # Base processed data directory
    base_processed_data_dir = os.path.join(project_dir, "data", "processed", name)
    if not os.path.isdir(base_processed_data_dir):
        os.makedirs(base_processed_data_dir)

    # Initialise pint's UnitRegistry
    ureg = UnitRegistry()

    # Load settings yaml file
    with open(settingsFile) as handle:
        settings = yaml.load(handle)

    # Final particle concentration
    outputUnit = ureg(settings['output']['unit'])

    # Sensors
    sensorsDict = settings['sensors']

    # Experimental conditions
    expDict = settings['exp']

    # Load information about sensors and load data for each sensor
    sensorsDict = loadSensorsData(sensorsDict, sensorsFile, outputUnit)

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
