USB-ISS
=======

SPI mode
--------

|----------+----------------+-------------+-------------+----------|
| SPI Mode | Clock Polarity | Clock Phase | Clock Edge  | USB-ISS  |
|          | (CPOL/CKP)     | (CPHA)      | (CKE/NCPHA) | SPI Mode |
|----------+----------------+-------------+-------------+----------|
| 0 (0,0)  | 0              | 0           | 1           | 0x90     |
|----------+----------------+-------------+-------------+----------|
| 1 (0,1)  | 0              | 1           | 0           | 0x92     |
|----------+----------------+-------------+-------------+----------|
| 2 (1,0)  | 1              | 0           | 1           | 0x91     |
|----------+----------------+-------------+-------------+----------|
| 3 (1,1)  | 1              | 1           | 0           | 0x93     |
|----------+----------------+-------------+-------------+----------|

The meaning is:

- CPOL:
  - 0 = Clock Idle low level
  - 1 = Clock Idle high level
- CPHA:
  - 0 = SDO transmit edge active to idle
  - 1 = SDO transmit edge idle to active

References
----------

- http://www.rosseeld.be/DRO/PIC/SPI_Timing.htm 
