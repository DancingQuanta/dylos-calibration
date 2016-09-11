Data Analysis
=============

After collecting data from the sensors which would be timeseries (data sampled over time), data can then be analysed.
There are different analyses such as comparing two Dylos sensors or calibrating a Dylos sensor against another sensor.

A Makefile will be used to manage the data analysis where it will run scripts from `src/`.
The scripts that Makefile will invoke requires YAML configuration files which contain information about the raw data of various sensors.
The YAML files contains the location of raw data, which pre-processing of the data needs to be done before analysis.

Calibration
^^^^^^^^^^^

For calibration of a Dylos sensor agaainst Grimm or Alphasense OPCN2, the YAML file needs to be in `calibration/`.
The structure of the YAML looks like this::


  sensors:
    calibratee:
      name: dylos
      sensor:
        path: "dylos-grimm/dumped-dylos.log"
        type: dylos
        timeshift: '-01:01:00'
    calibrater:
      name: grimm
      sensor:
        path: "dylos-grimm/grimm.log"
        type: grimm
        timeshift: '-00:07:00'
        resample: minute
      process:
        prunebins:
  output:
    report:
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


