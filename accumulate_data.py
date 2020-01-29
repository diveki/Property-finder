import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
from property import *

def get_averages(df):
    av = df.groupby(['city', 'type'])['city', 'type', 'land_size', 'price', 'size', 'unit_price'].apply(lambda g: g.mean(skipna=False)).reset_index()
    xx = df.groupby(['city', 'type'])['price'].count().reset_index()
    xx = xx.rename(columns={'price':'count'})
    av = av.merge(xx, on=['city', 'type'])
    av['Date'] = pd.datetime.today().strftime("%Y-%m-%d")
    av['Date'] = pd.to_datetime(av['Date'])
    av = av.set_index('Date')
    return av


def read_historical_data(fname):
    av_hist = pd.read_excel(fname)
    av_hist = av_hist.set_index('Date')
    colnames = av_hist.columns
    return av_hist, colnames

def download_data(par, save_name):
    df = pd.DataFrame()
    for spar in par:
        scraper = ScrapeDataIngatlan(dct=spar)
        scraper.get_properties()
        tmp = scraper.container.to_dataframe()
        df = pd.concat([df, tmp], sort=False)
        df.to_excel(save_name, index=False)
    return(df)


### Collect data

search_params = [
                 {'city': 'Szeged', 'property_type': 'haz', 'sale_type': 'elado'},
                 {'city': 'Algyo', 'property_type': 'haz', 'sale_type': 'elado'},
                 {'city': 'Morahalom', 'property_type': 'haz', 'sale_type': 'elado'},
                 {'city': 'Szeged', 'property_type': 'lakas', 'sale_type': 'elado'},
                 {'city': 'Szeged', 'property_type': 'garazs', 'sale_type': 'elado'}
                 ]


if __name__ == '__main__':
    date = dt.datetime.today()
    path_name = 'Data'
    save_name = os.path.join(path_name, date.strftime('%Y%m%d') + '_result.xlsx')

    df = download_data(search_params, save_name)
    df['Date'] = pd.to_datetime(date)
    df.to_excel(save_name, index=False)
    ### read averages from excel
    av_hist, avhist_colnames = read_historical_data('Averages/averages.xlsx')

    ### Calculate stats on the properties
    av = get_averages(df)
    av = av.loc[:,avhist_colnames]

    ### concatenate historical and recent data
    av = pd.concat([av_hist, av], sort=False)


    # save averages to excel
    av.to_excel('Averages/averages.xlsx', index=True)
