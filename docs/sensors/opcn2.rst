Alphasense OPC-N2
=================

Alphasense OPC-N2 is a optical particle counter.
The OPC continuously count the particles into their bin sizes within a defined sampling period.
The sensor also measures temperature, pressure, sample flow rate, PM1, PM2.5 and PM10.
To obtain the particle number concentration, divide the particle bin values by the product of flow rate and sampling period.
Please read the technical details carefully as it explains the limits of the sensor.

Technical details
-----------------

+-----------------------------+------------------------------------------------+------------+
| Particle range              | Spherical equivalent size (based on RI of 1.5) | 0.38 to 17 |
+=============================+================================================+============+
| Size categorisation         | Number of software bins                        | 16         |
+-----------------------------+------------------------------------------------+------------+
| Sampling period             | Histogram period (seconds)                     | 1.4 to 10  |
+-----------------------------+------------------------------------------------+------------+
| Total flow rate             | (typical) L/min                                | 1.2        |
+-----------------------------+------------------------------------------------+------------+
| Sample flow rate            | (typical) mL/min                               | 220        |
+-----------------------------+------------------------------------------------+------------+
| Max particle count rate     | Particles/second                               | 10000      |
+-----------------------------+------------------------------------------------+------------+
| Max particle total count    | Total counts per sample                        | 2^16       |
+-----------------------------+------------------------------------------------+------------+
| Max coincidence probability | %concentration at 10E6 particles/L             | 0.84       |
|                             | %concentration at 500 particles/L              | 0.24       |
+-----------------------------+------------------------------------------------+------------+
| Detection limits (PM10 )    | Minimum                                        | 0.01 ug/m3 |
|                             | Maximum                                        | 1500 mg/m3 |
+-----------------------------+------------------------------------------------+------------+

Since the sensors counts particle into individual size bins, the value of each bin have a limit, at 2^8.
This is the reason why it is recommended to sample the sensor at most 10 seconds.

Measurement
-----------

The sensor is SPI slave so the logger can query the data from the sensor.
The data is a histogram encoded in bytes and when decoded contains the following data::

  Bin0, Bin1, ... Bin15, Bin1MToF, Bin3MToF, Bin5MToF, Bin7MToF, SFR, Temp/Pres, Period, Checksum PM1, PM2.5, PM10, 

.. attribute:: Bin

 Total counts since last query as unsigned 16 integer

.. attribute:: MToF

  MToF is an unsigned 8bit integer that represents the average amount of time that particles sized in the stated bin took to cross the OPC's laser beam.
  Each value is in 1/3 us. i.e. a value of 10 would represent 3.33us.

.. attribute:: Sample flow rate (SRF)

  Sample Flow Rate is a float variable occupying 4 bytes that represents the sample flow rate in ml/s.

.. attribute:: Temperature/Pressure (Temp/Pres)

  The temperature and pressure is alternating in the data.

  Temperature is an unsigned 32bit integer that represents temperature in C multiplied by 10.

  Pressure is an unsigned 32bit integer that represents pressure in pascals.

.. attribute:: Sampling Period (Period)

  Sampling Period is a float variable occupying 4 bytes and is a measure of the histogram's actual sampling period in seconds.

.. attribute:: Checksum

  Checksum is an unsigned 16bit integer and is the least significant 16bits of the sum of the counts in all the histogram bins.

.. attribute:: PM

  PM1, PM2.5 and PM10 are float variables 4 bytes.
  Units are ug/m3.


Raspberry Pi
------------

I am using `dhhagan's py-opc module`_, a python library for controlling an Alphasense OPCN2.
Through the `py-opc` module, I am able to get configuration of the sensor from its onboard memory.
Part of that configuration is the bin boundaries which are ADC values which can be converted to micrometers using a  lookup table supplied by Alphasense and is included in `py-opc` for easy access.

Default bin boundaries
~~~~~~~~~~~~~~~~~~~~~~

The sensor reports the boundaries of the right side of bins between 0.38 and 17.5 um.

The bin boundaries in micrometers are::

  0.38, 0.54, 0.78, 1.05, 1.34, 1.59, 2.07, 3.0, 4.0, 5.0, 6.5, 8.0, 10.0, 12.0, 14.0, 16.0, 17.5

where all values except last is lower bin boundaries and the last value is upper bin boundary.

Logging
~~~~~~~

The program I wrote that logs from the alphasense OPC writes the following data to file::

  datetime, Bin0, Bin1, ..., Bin15, Bin1MToF, Bin3MToF, Bin5MToF, Bin7MToF, Sampling Period, Temperature, Pressure, PM1, PM2.5, PM10

.. attribute:: datetime

  Date and time of the data taken.



.. todo::

  Understand what is max coincidence probability


.. _`dhhagan's py-opc module`: https://github.com/waggle-sensor/waggle

