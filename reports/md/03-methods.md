
# Methodology

The calibration of Dylos were performed on two separate ocassions; first against Grimm and second against Alphasense.
The calibration was carried out in a simple clip on lid plastic box as shown in +@box.
The lid is not air-tight which allows circulation of air out of the box.
A solution of calibration particles was vapourised by a nebuliser and was injected into the box through the middle of the lid.

Each of the instruments was connected to a Raspberry Pi, as well as a monitor to monitor the output of the instruments.
A custom Python script on the Raspberry Pi logs the measurements from the instruments and displays them on the monitor.

The calibration process involves running the nebuliser without a calibration particle solution so that clean filtered air is injected into the box which pushes the resident air out of the box.
When the readings of the instruments reaches near zero particles, a solution of calibration particle of a chosen size is introduced to the nebuliser.
The particles is allowed to populate the box for more than 30 minutes before removing the solution.
The process repeats for each solution of particles of different sizes.

Analysis

Rebin

Correlation

