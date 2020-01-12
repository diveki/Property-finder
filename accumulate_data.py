import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from property import *

def get_averages(df):
    av = df.groupby(['city', 'type']).apply(lambda g: g.mean(skipna=False)).reset_index()
    av['Date'] = pd.datetime.today()
    av['Date'] = pd.to_datetime(av['Date'])
    av = av.set_index('Date')
    return av

def read_historical_data(fname):
    av_hist = pd.read_excel(fname)
    av_hist = av_hist.set_index('Date')
    colnames = av_hist.columns
    return av_hist, colnames


### Collect data

search_params = [
                #  {'city': 'Szeged', 'property_type': 'haz', 'sale_type': 'elado'},
                 {'city': 'Algyo', 'property_type': 'haz', 'sale_type': 'elado'},
                 {'city': 'Morahalom', 'property_type': 'haz', 'sale_type': 'elado'},
                #  {'city': 'Szeged', 'property_type': 'lakas', 'sale_type': 'elado'},
                 {'city': 'Szeged', 'property_type': 'garazs', 'sale_type': 'elado'}
                 ]

df = pd.DataFrame()
for spar in search_params:
    scraper = ScrapeDataIngatlan(dct=spar)
    scraper.get_properties()
    tmp = scraper.container.to_dataframe()
    df = pd.concat([df, tmp])

### read averages from excel
av_hist, avhist_colnames = read_historical_data('averages.xlsx')

### Calculate stats on the properties
av = get_averages(df)
av = av.loc[:,avhist_colnames]

### concatenate historical and recent data
av = pd.concat([av_hist, av], sort=False)


# save averages to excel
av.to_excel('averages.xlsx', index=True)
