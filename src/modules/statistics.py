def stats(counts, midpoints):
    """Statistics for binned data

    Args:
        counts: ndarray
        midpoints: adarray

    Returns:

    """
    # Totoal counts
    totalCounts = np.sum(counts)

    # Mean
    mean = np.sum(counts * midpoints) / totalCounts

    # Standard deviation
    std = np.sum(counts * ((midpoints - mean) ** 2)) / totalCounts

    # Lower 95% bounds
    lower = mean - 2 * std

    # Upper 95% bounds
    upper = mean + 2 * std

    return mean, std, lower, upper

def histstd(data, bounds, mean):
    """Calculate standard deviation of a binned data
    Args:
        data : list
            list of counts per bin
        bins : list
            list of bin boundaries, with length one element longer than data
        mean : float

    Returns:
        std : float
            Standard deviation
    """
    numerator = 0
    totalCounts = 0
    for ix, key in enumerate(data):
        counts = data[ix]
        lower = bounds[ix]
        upper = bounds[ix+1]
        difference = upper-lower
        midpoint = lower + difference/2
        totalCounts = totalCounts + counts
        numerator = counts * ((midpoint - mean) ** 2) + numerator

    denominator = totalCounts
    std = np.sqrt(numerator / denominator)
    return std, lower, upper

def geometricStd(data, bounds, gmd):
    """Calculate geometric standard deviation of a lognormal distribution
    Args:
        data : list
            list of counts per bin
        bins : list
            list of bin boundaries, with length one element longer than data
        gmd : float
            Geometric mean diameter

    Returns:
        gsd : float
            Geometric standard deviation
    """
    # Geometric standard deviation
    numerator = 0
    totalCounts = 0
    for ix, key in enumerate(data):
        counts = data[ix]
        lower = bounds[ix]
        upper = bounds[ix+1]
        difference = upper-lower
        midpoint = lower + difference/2
        logmidpoint = np.log10(midpoint)  # Is this correct? todo
        totalCounts = totalCounts + counts
        numerator = counts * ((logmidpoint - np.log10(gmd)) ** 2) + numerator

    denominator = totalCounts - 1
    loggsd = np.sqrt(numerator / denominator)
    gsd = np.exp(loggsd)

    # Lower 95% bounds
    lower = gmd / (gsd ** 2)

    # Upper 95% bounds
    upper = gmd * (gsd ** 2)

    return gsd, lower, upper


def normalise(data, bins):
    for key in bins:
        value = bins[key]
        if isinstance(value,  tuple):
            if len(value) == 2:
                lower = value[0]
                upper = value[1]
                difference = upper-lower
                data[key] = data[key]/difference
            else:
                error = "The length of value of the key %s is %s,  must be 2" % (key, len(value))
                print(error)
        else:
            error = "The type of value of the key %s is %s,  must be tuple e.g. (1, 2)" % (key, type(value))
            print(error)
    return data



