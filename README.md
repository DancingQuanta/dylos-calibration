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
    └── src                <- Source code for use in this project.
        ├── __init__.py    <- Makes src a Python module
        │
        ├── data           <- Scripts to process data
        │   └── inspect_data.py
        │
        ├── docs           <- Scripts for report generation
        │   └── gen.py     <- Uses Jinja2 and a tamplate
        │  
        ├── modules        <- Own python modules
        │   ├── __init__.py
        │   ├── orderedDictYAML.py
        │   └── tools.py
        │
        └── sensors        <- Scripts and details for individual sensors
            ├── dylos.py
            ├── dylos-plots.py
            ├── grimm.py
            └── sensors.yaml

