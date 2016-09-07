# def changeExt(path, ext):
    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]+ext
    return filename

# def pathGen(path):
    # if not os.path.isdir(path):
        # os.makedirs(path)

# def dataPathGen(path):
    # path = os.path.join(path, "data")
    # if not os.path.isdir(path):
        # os.makedirs(path)
    # return path

# def statsPathGen(path):
    # path = os.path.join(path, "stats")
    # if not os.path.isdir(path):
        # os.makedirs(path)
    # return path

# def plotsPathGen(path):
    # path = os.path.join(path, "plots")
    # if not os.path.isdir(path):
        # os.makedirs(path)
    # return path

def analyse(data, savepath, filename):
    """Plot input data and subtract the larger sizes from smaller sizes.
    Also print the input data to file for diagonistics purposes.

    """

    print(filename)
    writeData(data,savepath,filename)
    plot(data,savepath,filename)
    realData = realCounts(data)
    filename = "real_" + filename
    writeData(data,savepath,filename)
    plot(realData,savepath,filename)
    return realData

