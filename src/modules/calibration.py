
def rebin(bins1,bins2):
    """Rebin binned data to new bin boundaries

    Args:
        df1 : Pandas.DataFrame or Pandas.Series
            Each column of DataFrame is a bin of data.
            This Dataframe is to be rebinned.
            Pandas.Series will be converted into Pandas.DataFrame before
            rebinning.
        bins1 : dict of str: list, str: list
            Input dict with two key-value pairs; 'columns' and 'bounds'.
            Value of 'column' is list of strings denoting columns.
            Value of 'bounds' is list of low bin boundary positions, with the
            last element being the top boundary of last bin.
            This dict defines the current boundaries of input bin data.
        bins2 : dict of str: list, str: list
            Input dict with two key-value pairs; 'columns' and 'bounds'.
            This dict have same structure as bins1 and defines the new bin
            boundaries of the binned data.

    Return:
        df2: Pandas.DataFrame
            Output dataframe with newly changed bin boundaries.

    """

    # Generate bin labels for final set of bins
    # but first extract the string before dash in column names of initial data.
    string = bins1['data'].columns[0].split('-')
    label = string[0]
    bins2 = generateBinLabels(bins2, label)

    # Check for a series or dataframe
    if isinstance(bins1['data'], pd.Series):
        bins1['data'] = pd.DataFrame([bins1['data']])

    # columns1 = bins1['columns']
    # bounds1 = bins1['bounds']
    # columns2 = bins2['columns']
    # bounds2 = bins2['bounds']

    # Initialise new dataframe
    bins2['data'] = pd.DataFrame(0, index=bins1['data'].index, columns=bins2['columns'])
    for ix2, key2 in enumerate(bins2['columns']):
        for ix1, key1 in enumerate(bins1['columns']):
            lower1 = bins1['bounds'][ix1]
            upper1 = bins1['bounds'][ix1+1]
            diff1 = upper1 - lower1
            lower2 = bins2['bounds'][ix2]
            upper2 = bins2['bounds'][ix2+1]
            diff2 = upper2 - lower2

def calibrate(df):
    """Calibrate
    """
    # Take mean of a dateset
    mean = df.mean()
    df1 = mean
    index = mean.index
    k = 0
    for i,a in enumerate(index):
        for j,b in enumerate(index[i:]):
            first = a.split('-')
            second = b.split('-')
            if first[1] == second[1] and first[0] != second[0]:
                c = "%s/%s" % (a, b)
                d = mean.loc[a] / mean.loc[b]
                df1.loc[c] = d
                # c[k] = {"%s/%s" % (a, b) : mean.loc[a] / mean.loc[b]}
                k += 1
    print(df1)
    return mean


def calibrate(df):
    """Calibrate
    """
    # Take mean of a dateset
    mean = df.mean()
    df1 = mean
    index = mean.index
    k = 0
    for i,a in enumerate(index):
        for j,b in enumerate(index[i:]):
            first = a.split('-')
            second = b.split('-')
            if first[1] == second[1] and first[0] != second[0]:
                c = "%s/%s" % (a, b)
                d = mean.loc[a] / mean.loc[b]
                df1.loc[c] = d
                # c[k] = {"%s/%s" % (a, b) : mean.loc[a] / mean.loc[b]}
                k += 1
    print(df1)
    return mean

def rebin(bins1,bins2):
    """Rebin binned data to new bin boundaries

    Args:
        df1 : Pandas.DataFrame or Pandas.Series
            Each column of DataFrame is a bin of data.
            This Dataframe is to be rebinned.
            Pandas.Series will be converted into Pandas.DataFrame before
            rebinning.
        bins1 : dict of str: list, str: list
            Input dict with two key-value pairs; 'columns' and 'bounds'.
            Value of 'column' is list of strings denoting columns.
            Value of 'bounds' is list of low bin boundary positions, with the
            last element being the top boundary of last bin.
            This dict defines the current boundaries of input bin data.
        bins2 : dict of str: list, str: list
            Input dict with two key-value pairs; 'columns' and 'bounds'.
            This dict have same structure as bins1 and defines the new bin
            boundaries of the binned data.

    Return:
        df2: Pandas.DataFrame
            Output dataframe with newly changed bin boundaries.

    """

    # Generate bin labels for final set of bins
    # but first extract the string before dash in column names of initial data.
    string = bins1['data'].columns[0].split('-')
    label = string[0]
    bins2 = generateBinLabels(bins2, label)

    # Check for a series or dataframe
    if isinstance(bins1['data'], pd.Series):
        bins1['data'] = pd.DataFrame([bins1['data']])

    # columns1 = bins1['columns']
    # bounds1 = bins1['bounds']
    # columns2 = bins2['columns']
    # bounds2 = bins2['bounds']

    # Initialise new dataframe
    bins2['data'] = pd.DataFrame(0, index=bins1['data'].index, columns=bins2['columns'])
    for ix2, key2 in enumerate(bins2['columns']):
        for ix1, key1 in enumerate(bins1['columns']):
            lower1 = bins1['bounds'][ix1]
            upper1 = bins1['bounds'][ix1+1]
            diff1 = upper1 - lower1
            lower2 = bins2['bounds'][ix2]
            upper2 = bins2['bounds'][ix2+1]
    print(calibration)
mean.loc[a] / mean.loc[b]
