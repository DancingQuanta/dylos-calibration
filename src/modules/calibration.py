
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


