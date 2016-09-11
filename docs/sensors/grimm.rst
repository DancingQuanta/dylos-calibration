Grimm 1.108
===========

The Grimm have various sampling frequencies and in this investigation the sample frequency is set to every 6 seconds where the measured particle counts in each bin is particle per 100 ml.

In this mode the data transmitted have three unique types of data string: P, C (small) and c (big).

      Year  Mon  Day  Hr  Min  Loc  GF   Err Qbatt  Im  UeL  Ue4  Ue3  Ue2  Ue1  Iv
  P   16    7    4    0   7    2    23   0   130    30  197  1    0    0    0    6
  C00      60       30        5        0        0        0        0        0 
  c00       0        0        0        0        0        0        0        0 

The data in P contains the date and time down to minute resolution as well other diagnostic information about the Grimm instrument.
The line beginning with C contains particle counts of small particles from 0.3 um to 2um separated into 8 bins.
The line beginning with c contain particle counts of big particles from 2um to 20um um separated into 8 bins.
Both the C and c begin with two digits, the first is the multiple of 6 seconds and second the number of seconds from 0 to 5.

The flow rate of particles pass the laser is 1.2 l/min.


Grimm particle size range
-------------------------

The Grimm measure particle counts over a size range of 0.3 um to 20 um in 16 bins.
From the Technical section, the size are separated into bins by channels which are quoted as follows:

  0.3/ 0.4/ 0.5/ 0.65/ 0.8/ 1.0/ 1.6/ 2/ 3/ 4/ 5/ 7.5/ 10/ 15/ 20

Since there are 16 bins, the first bin is 0.23um and is estimated with lognormal distribution and so can be ignored.

The measured size distribution of the aerosol particles could be used to find the particle mass distribution.
Within measuring mode “particle mass” an additional size channel is arithmetically adjoined below the smallest size channel.

The given channel thresholds are valid for a count efficiency ratio of 50% with mono-disperse latex aerosol.
