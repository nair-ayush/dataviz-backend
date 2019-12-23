import pandas as pd

def dimensions( df):
    return list(df.shape)
def summary(df):
    # print(df.describe())
    return df.describe().to_dict(orient='records')