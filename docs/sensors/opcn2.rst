Alphasense OPC-N2
=================

Technical details
-----------------

+-----------------------------+------------------------------------------------+------------+
| Particle range              | Spherical equivalent size (based on RI of 1.5) | 0.38 to 17 |
+=============================+================================================+============+
| Size categorisation         | Number of software bins                        | 16         |
+-----------------------------+------------------------------------------------+------------+
| Sampling interval           | Histogram period (seconds)                     | 1.4 to 10  |
+-----------------------------+------------------------------------------------+------------+
| Total flow rate             | (typical) L/min                                | 1.2        |
+-----------------------------+------------------------------------------------+------------+
| Sample flow rate            | (typical) mL/min                               | 220        |
+-----------------------------+------------------------------------------------+------------+-----+
| Max particle count rate     | Particles/second                               | 10         | 000 |
+-----------------------------+------------------------------------------------+------------+-----+
| Max coincidence probability | %concentration at 10 6 particles/L             | 0.84       |
|                             | %concentration at 500 particles/L              | 0.24       |
+-----------------------------+------------------------------------------------+------------+
| Detection limits (PM10 )    | Minimum                                        | 0.01 ug/m3 |
|                             | Maximum                                        | 1500 mg/m3 |
+-----------------------------+------------------------------------------------+------------+

Raspberry Pi
------------

I am using `dhhagan's py-opc module`_, a python library for controlling an Alphasense OPCN2.


Default bin boundaries
----------------------

Through the `py-opc` module, I am able to get configuration of the sensor from its onboard memory.
Part of that configuration is the bin boundaries which are ADC values and included in the py-opc module is a lookup table between ADC and micrometers particle size.

The bin boundaries in micrometers are

.. hlist::
  :columns: 8

  - 0.54
  - 0.78
  - 1.05
  - 1.34
  - 1.59
  - 2.07
  - 3.0
  - 4.0
  - 5.0
  - 6.5
  - 8.0
  - 10.0
  - 12.0
  - 14.0
  - 16.0
  - 17.0

where the all except last is lower bin boundaries and the last value is upper bin boundary.

.. todo::

  Understand what is max coincidence probability


.. _`dhhagan's py-opc module`: https://github.com/waggle-sensor/waggle

