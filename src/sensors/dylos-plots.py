#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.tools import *

# Plot a Dylos dataset against another

if __name__ == '__main__':
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    raw_data_dir = os.path.join(project_dir, "data", "raw")
    for file in os.listdir(raw_data_dir):
        for file1 in os.listdir(raw_data_dir):
            if file.endswith(".log") and file1.endswith(".log"):
                if "dylos" in file and "dylos" in file1:
                    print(file + " " + file1)
                    filename = os.path.splitext(file)[0]
                    filename1 = os.path.splitext(file1)[0]
                    path = os.path.join(raw_data_dir, file)
                    path1 = os.path.join(raw_data_dir, file1)
                    data = loadDylosData(path)
                    data1 = loadDylosData(path1)

                    img_dir = os.path.join(project_dir, "imgs", "twodylos")
                    if not os.path.isdir(img_dir):
                        os.makedirs(img_dir)
                    filename2 = filename + "-" + filename1
                    twoPlots(data,data1,img_dir,filename2)
                    filename2 = "real-" + filename2
                    twoPlots(data,data1,img_dir,filename2)
