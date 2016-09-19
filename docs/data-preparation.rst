Preparing data
==============

Data produced by Dylos and collected by AirPi needs to be checked first before analysis.
The data collected by AirPi is stored in a hourly dataset for each sensor.
The data files should have the format YYYY-MM-DD-HH-dev where dev is nickname of the sensor.

Dylos DC1100 and Dylos DC1700
-----------------------------

If you are running an experiment where you are using Dylos DC1100 and Dylos DC1700.
The device names assigned to each sensor depends on which sensor is plugged in first.
At any time, the device names may change, due to unplugging and replugging or OS misbehaving, the data from both sensor may get mixed up in a data file.
So those data files needs to be separated out properly.

1. It was known that Dylos DC1100 Pro have a sampling period of 59 seconds while Dylos DC1700 have a sampling period of 60 seconds. So to separate them out I have to look at the timestamp and see if the timestamps change by 60 or 59 seconds.
2. Concatenate the data files in one file for each sensor, for example, I simply ran a linux command::

    cat *-Dylos > Dylos
    cat *-Dylos1 > Dylos1

3. Read the timestamp manually to find the place where the timestamps' frequency changes.
   Or run a script that can find changes in frequency of timestamps.
   Note this timestamp, which is usually separated in time from previous timestamp by more than one minute.
   An example of this step is shown below::

    2016-09-08 09:09:04.438688,3231,1328 |
    2016-09-08 09:10:04.532087,3387,1363 | The data here comes from DC1700
    2016-09-08 09:11:07.999879,3933,1622 |
    2016-09-08 09:12:09.636218,4235,1760 |
    2016-09-08 09:13:17.006168,4358,1879 |
    2016-09-08 09:14:05.726325,4323,1807 |
    2016-09-08 09:15:34.276283,4222,1783 |
    2016-09-08 09:16:04.434857,4246,1800 |
    2016-09-08 09:17:04.435173,4440,1854 |
    2016-09-08 09:18:04.436010,4460,1880 |
    2016-09-08 09:19:04.433568,4483,1883 |
    2016-09-08 09:20:05.616240,4504,1891 <---------- The frequency of the timestamp changed here
    2016-09-08 09:23:58.366434,4692,1529 <---------- 
    2016-09-08 09:24:54.972582,4644,1534 | Notice there is 3 mins difference between this timestep and the previous
    2016-09-08 09:25:55.066175,4611,1511 | This is probably where the sensors may got unplugged, pi lazy or
    2016-09-08 09:26:52.810112,4655,1502 | logger restarted.
    2016-09-08 09:27:56.999825,4648,1507 | 
    2016-09-08 09:28:50.999911,4651,1474 |
    2016-09-08 09:29:49.652145,4532,1491 | The data here comes from DC1100
    2016-09-08 09:30:48.603234,4597,1496 |
    2016-09-08 09:31:47.530692,4593,1473 | The seconds of timestamp decrease by one every minute.
    2016-09-08 09:32:46.479580,4588,1508 |
    2016-09-08 09:33:45.423676,4659,1477 |

4. Make a copy of the full dataset and then delete the data in one copy behind the identified timestamp and delete the data in other copy after the timestamp.

Next to data analysis!
