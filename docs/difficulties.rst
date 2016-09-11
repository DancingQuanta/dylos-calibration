Difficulties in the project
===========================


Raspberry pi and the current software implemented in python are not suitable for logging data from Dylos and Grimm particle counters.
Although the logic was trivial, the difficulties lies in the fact that Pi have a multi-processor which means that it performs operations not in real time.
Thus the Pi does not write the data it receives from the sensors to disk in regular intervals.
This causes the data to be missing in some time periods and the intervals between data points is not always consistent. 

The above difficulties outweighs any advantage of Raspberry Pi as an automatic logger which logs all data from a number of sensors in one place.
Plus both Dylos and Grimm sensors have their own timing mechanisms, they probably use a Real Time Clock, and they continually output data in consistent time intervals.
However Dylos does not output the timestamp along with the particle counts data and the only way to receive the data with timestamp is to let it logs the data for the time period of the investigation and then dumps the data which contain the timestamps with the particle counts.


Sometimes the Raspberry Pi decides to stop the program for a while then switched the serial ports. This seems to happen to Dylos sensors and so don't not touch Grimm somehow. But the consequence of this is that the data files got mixed data from both Dylos sensors.



