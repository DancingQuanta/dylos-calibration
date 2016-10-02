
Aerosol Measurement and Dylos calibration
==============================

Measures the concentration of calibration nanospheres with various sensors and calibrate Dylos Sensor

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile to manage analysis and report generation
    ├── README.md          <- The top-level README.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final dataset.
    │   └── raw            <- The original, immutable data dump.
    |
    ├── imgs               <- Generated graphics and figures to be used in reporting
    │
    ├── docs               <- A MkDocs documentation
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to process data
    │   │
    │   ├── docs           <- Scripts for report generation
    │   │   └── gen.py     <- Uses Jinja2 and a tamplate
    │   │  
    │   ├── visualisation  <- Analyse and visualise data
    │   │
    │   └── sensors        <- Scripts and details for individual sensors
    │
    ├── conditions         <- Store experimental conditions in yaml
    │   ├── particles.yaml <- Particle size aliases and units
    │   └── sensors.yaml   <- Characteristics of sensors
    │ 
    ├── settings           <- Store details about data for each experiment
    │
    └── templates          <- Jinja templates for displaying results


Credits
-------

This project is part of a NERC's placement at University of Leeds during Summer of 2016.

