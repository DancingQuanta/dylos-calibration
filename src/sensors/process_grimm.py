#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Decode grimm dataset

import os
import sys
from datetime import datetime as dt
import csv

def argparse(argv):
    inputfile = ''
    outputfile = ''
    try:
        inputfile = str(argv[1])
        outputfile = str(argv[2])
    except:
        error = argv[0] + " <inputfile> <outputfile>"
        print(error)
        sys.exit(2)
    if os.path.isfile(inputfile):
        if not os.path.isfile(outputfile):
            print('Input file is', inputfile)
            print('Output file is', outputfile)
            return inputfile,outputfile
        else:
            print("Outputfile already exist")
            sys.exit(2)
    else:
        print("Inputfile does not exist")
        sys.exit(2)

def main(inputfile, outputfile):
    with open(inputfile) as input_file:
        with open(outputfile, 'w') as output_file:
            transform(input_file,output_file)
    print("Written data to " + outputfile + " successfully!")
    sys.exit("Done!")

def transform(input,output):
    out = csv.writer(output)
    firstP = 0
    for line in input:
        parts = line.split()
        print(parts)
        id = parts[0]
        if id == "P": # Read date and time
            year,month,day,hour,min = parts[1:6]
            year = "20" + year
            firstP = 1
        elif firstP == 1: # Read bin data
            c = id[0] # C or c?
            if c == "C":
                bin_data = parts[1:]
            elif c == "c":
                six = int(id[1]) # Increment every six seconds
                second = int(id[2]) # Increment every second
                bin_data = bin_data + parts[1:]
                second = second + six*6 # Calculate true seconds
                print(year)
                datetime = dt(int(year),int(month),int(day),int(hour),int(min),second)
                data = [str(datetime)] + bin_data
                print(data)
                out.writerow(data)

if __name__ == "__main__":
    inputfile,outputfile = argparse(sys.argv)
    main(inputfile, outputfile)
