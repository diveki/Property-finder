import pandas as pd
import os
import numpy as np
from bs4 import BeautifulSoup
import requests


class Property:
    def __init__(self, dct={}):
        self.size            = dct.get('size', np.nan)
        self.url             = dct.get('url', '')
        self.city            = dct.get('city', '')
        self.street          = dct.get('street', '')
        self.price           = dct.get('price', np.nan)
        self.price_ccy       = dct.get('price_ccy', '')
        self.condition       = dct.get('condition', '')
        self.construction_year = dct.get('construction_year', np.nan)
        self.description     = dct.get('description', '')
        self.coordinates     = dct.get('coordinates', '')
        self.unit_price      = dct.get('unit_price', np.nan)
        self.unit_price_unit = dct.get('unit_price_unit', '')
        self.advertiser      = dct.get('advertiser', {})


class House(Property):
    def __init__(self, dct={}):
        Property.__init__(dct=dct)
        self.property_size   = dct.get('property_size', np.nan)
        self.land_size       = dct.get('land_size', np.nan)
        self.room_number     = dct.get('room_number', np.nan)
        self.comfort         = dct.get('comfort', '')
        self.energy_certificate = dct.get('energy_certificate', '')
        self.stair_number    = dct.get('stair_number', np.nan)
        self.heating         = dct.get('heating', '')
        self.aircondition    = dct.get('aircondition', '')
        self.bathroom        = dct.get('bathroom', '')
        self.view            = dct.get('view', '')
        self.attic           = dct.get('attic', '')
        self.cellar          = dct.get('cellar', '')
        self.parking         = dct.get('parking', '')
        self.garage          = Garage(dct=dct)


class Garage(Property):
    def __init__(self, dct={}):
        Property.__init__(dct=dct)


class Advertiser:
    def __init__(self, dct={}):
        self.name   = dct.get('name', '')
        self.phone  = dct.get('phone', '')
        self.agency = dct.get('agency', '')


class PropertyContainer:
    def __init__(self):
        self._item = list()

    def add(self, prop):
        self._item.append(prop)

    def __getitem__(self, key):
        return self._item[key]

    def __len__(self):
        return len(self._item)


class PropertyContainerIterator:
   ''' Iterator class '''
   def __init__(self, prop):
       # Team object reference
       self._prop = prop
       # member variable to keep track of current index
       self._index = 0

   def __next__(self):
       ''''Returns the next value from team object's lists '''
       if self._index < len(self._prop._item):
           result = self._prop._item[self._index]
           self._index +=1
           return result
       # End of Iteration
       raise StopIteration
