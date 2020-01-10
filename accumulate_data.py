import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from property import *

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

