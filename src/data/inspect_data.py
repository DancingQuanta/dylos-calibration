#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.tools import *

# Inspect data for any missing datetime and non numeric type.

# # Checking non numeric data
# # data = grimmData['5-Grimm']
# # for i in range(0,200):
    # # value = data.iloc[i]
    # # if isinstance(value,object):
        # # print(i)

if __name__ == '__main__':
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    raw_data_dir = os.path.join(project_dir, "data", "raw")
    for file in os.listdir(raw_data_dir):
        if file.endswith(".log"):
            print(file)
            filename = os.path.splitext(file)[0]
            path = os.path.join(raw_data_dir, file)
            if "grimm" in filename:
                data = loadGrimmData(path)
            elif "dylos" in filename:
                data = loadDylosData(path)
                data.index = data.index.values.astype('<M8[m]')
            else:
                error = "No log file with string \"grimm\" or \"dylos\""
                print(error)
                continue

            interim_data_dir = os.path.join(project_dir, "data", "interim", filename)
            if not os.path.isdir(interim_data_dir):
                os.makedirs(interim_data_dir)
            img_dir = os.path.join(project_dir, "imgs", filename)
            if not os.path.isdir(img_dir):
                os.makedirs(img_dir)

            filename1 = filename + ".csv"
            gaps = findGaps(data)
            print(gaps)
            print(interim_data_dir)
            print(filename1)
            groups = segments(data, interim_data_dir, filename1)
            print(groups)
            plot(data, img_dir, filename)
            data = realCounts(data)
            filename1 = "real_" + filename
            plot(data, img_dir, filename1)

