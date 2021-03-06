Data Analysis
============================================

The script `calibration.py` in `src` analyse the data from two sensors, one sensor to be calibrated and other sensor as a reference.
The script loads a YAML configuration file which contain information about the datasets and sensors.
This YAML file is stored in `calibration/` and can have any filename but must have `.yaml` extension.
The script `calibration.py` will produce a JSON file that contains urls of the figures generated by `calibration.py` and other resulting data for reading.
A script `gen.py` in `src/docs` use this JSON file and a jinja latex template to generate a report.
The data from JSON file will be put in relevant places in the template.
Finally a Makefile is used to execute the scripts.
There are three important make commands to use:

.. option:: make cali

  Execute whole batch of scripts including `calibration.py` and `gen.py` to generate a resulting PDF report.

.. option:: make recali

  Same as `cali` but remove the processed output and starts again.

.. option:: make clean

  Remove all processed outputs.

The calibration YAML file have the following structure:

.. code-block:: yaml

  sensors:
    calibratee:
      id: dylos
      path: "dylos-grimm/dumped-dylos.log"
      type: dylos
      timeshift: '-01:01:00'
    calibrater:
      id: grimm
      path: "dylos-grimm/grimm.log"
      type: grimm
      timeshift: '-00:07:00'
      resample: minute
      prunebins:
  output:
    author: Andrew Tolmie
    title: Aerosol calibration of Dylos and Grimm
    concentration: '1 litre'
  exp:
    order: ["0.3", "0.8"]
    conditions:
      "0.3":
        time:
          start: 2016-07-04 09:30:00
          end: 2016-07-04 10:30:00
      "0.8":
        time:
          start: 2016-07-05 09:45:00
          end: 2016-07-05 10:15:00


`sensors` field
~~~~~~~~~~~~~~~

  Root configuration for sensors such as calibrater and calibratee.

.. py:attribute:: calibrater

  A reference sensor which a calibratee will be calibrated against.

.. py:attribute:: calibratee

  A sensor which will be calibrated by a calibrater

.. py:attribute:: type

  Set the type of the sensor so that the relevant information about the sensor can be fetched from `sensors.yaml` for use in data analysis.

.. py:attribute:: path

  Relative path from `data/raw` to the dataset produced by a sensor.

.. py:attribute:: timeshift

  If a dataset is not aligned in time, then the time could be shifted.
  
  For negative shift use the value `-00:00:00`

  For positive shift use the value `+00:00:00`

.. py:attribute:: resample: minute

  Resamples a dataset to different time frequency such as minutes.

.. py:attribute:: prunebins

  Remove a bin if it produces near zero mean over a chosen range, useful for plotting as the number of lines will be fewer.


`output` field
~~~~~~~~~~~~~~

  Configuration for the latex and odf output.

.. py:attribute:: concentration

  The final concentration unit the data must be displayed in.

.. py:attribute:: author

  Name of author

.. py:attribute:: title

  Title of report

`exp` field
~~~~~~~~~~~

  Configuration that choose a range of time series data to analyse.
  Different experimental conditions such as particle sizes are done at different times so the data must be chosen within a time range for a particular experimental condition for analysis.

.. py:attribute:: order

  Order of experimental conditions to be analysed.

.. py:attribute:: condiitons

  List of experimental conditions with start and end timestamp which will be used to select a range of data for analysis.

