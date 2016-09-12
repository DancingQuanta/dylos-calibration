Data Analysis
=============

After collecting data from the sensors which would be timeseries (data sampled over time), data can then be analysed.
There are different analyses such as comparing two Dylos sensors or calibrating a Dylos sensor against another sensor.

A Makefile will be used to manage the data analysis where it will run scripts from `src/`.
The scripts that Makefile will invoke requires YAML configuration files which contain information about the raw data of various sensors.
The YAML files contains the location of raw data, which pre-processing of the data needs to be done before analysis.
The `sensors.yaml` in `src/sensors/` contains information about sensors used in this investigation, what particle concentration do they produce, air flow rate, full name of sensor etc.

The results of the analysis will be produced in a PDF using latex and jinja2.

