
# Aerosol measuring instruments

Dylos DC1700 is a cheap customer-grade air quality monitor, priced at \SI{425.00}{\$} and measures the number of particles in two size ranges; $>\SI{0.5}{\um}$ and $>\SI{2.5}{\um}$.
The monitor output an average number of particles per 0.01 cubic foot every minute for each size range.
The measured concentration is displayed on a screen or through a serial output to which a computer can log data to a file.
The Dylos is battery powered which last for 6 hours and have a memory storage which store data for approximately whole week.

The Grimm 1.108 is a portable aerosol spectrometer (PAS) which is more expensive than the Dylos.
The Grimm measures the particle concentration over a size range of 0.3 um to 20 um in 15 bins.
The Grimm have various sampling frequencies and in this investigation the sample frequency is set to every 6 seconds 
which gives particle concentration in particles per \SI{100}{\ml}.

Alphasense OPC-N2 is a new OPC, having been released to the market in 2015, and is highly configurable.
The Alphasense measures the particle concentration over a size range of \SI{0.38}{\um} to \SI{17.5}{\um} in 16 bins.
The alphasense communicates with a computer via Serial Peripheral Interface (SIP) and allows an user to configure its bin boundaries, laser power and fan power.
The sensor returns a histogram of number of particles counted in a sample period when polled, as well as measured sample flow rate, temperature, pressure and sample period.
The sample period is the time between polling.
The user have to compute the particle concentration by dividing the particle count by the product of sample flow rate and sample period.

The properties of the aerosol measuring instruments is listed in +@tbl:properties.

+---------------------------------------+--------------+-------------+-------------------+
| Properties                            | Dylos DC1700 | Grimm 1.108 | Alphasense OPC-N2 |
+=======================================+==============+=============+===================+
| Particle range/\si{\um}               | 0.5 to 10    | 0.3 to 20   | 0.38 to 17        |
+---------------------------------------+--------------+-------------+-------------------+
| Number of bins                        | 2            | 15          | 16                |
+---------------------------------------+--------------+-------------+-------------------+
| Sampling period /\si{s}               | 60           | 6           | 10                |
+---------------------------------------+--------------+-------------+-------------------+
| Sample flow rate /\si{\cubic \cm/ \s} | 17.9         | 20          | 3.7               |
+---------------------------------------+--------------+-------------+-------------------+

Table: The properties of aerosol measuring instruments. {#tbl:properties}

