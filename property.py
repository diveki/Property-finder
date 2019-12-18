import pandas as pd
import os
import numpy as np
from bs4 import BeautifulSoup
import requests
import urllib
import re
import tqdm


class Property:
    def __init__(self, dct={}):
        self.size            = dct.get('size', None)
        self.url             = dct.get('url', None)
        self.city            = dct.get('city', None)
        self.street          = dct.get('street', None)
        self.price           = dct.get('price', None)
        self.price_ccy       = dct.get('price_ccy', None)
        self.condition       = dct.get('condition', None)
        self.construction_year = dct.get('construction_year', None)
        self.description     = dct.get('description', None)
        self.coordinates     = dct.get('coordinates', None)
        self.unit_price      = dct.get('unit_price', None)
        self.unit_price_unit = dct.get('unit_price_unit', None)
        self.advertiser      = dct.get('advertiser', None)


class House(Property):
    def __init__(self, dct={}):
        Property.__init__(self,dct=dct)
        self.land_size       = dct.get('land_size', None)
        self.room_number     = dct.get('room_number', None)
        self.comfort         = dct.get('comfort', None)
        self.energy_certificate = dct.get('energy_certificate', None)
        self.stair_number    = dct.get('stair_number', None)
        self.heating         = dct.get('heating', None)
        self.aircondition    = dct.get('aircondition', None)
        self.bathroom        = dct.get('bathroom', None)
        self.view            = dct.get('view', None)
        self.attic           = dct.get('attic', None)
        self.cellar          = dct.get('cellar', None)
        self.parking         = dct.get('parking', None)
        self.garage          = dct.get('garage', None)


class Garage(Property):
    def __init__(self, dct={}):
        Property.__init__(self, dct=dct)


class Advertiser:
    def __init__(self, dct={}):
        self.name   = dct.get('name', None)
        self.phone  = dct.get('phone', None)
        self.agency = dct.get('agency', None)


class PropertyContainer:
    def __init__(self):
        self._item = list()

    def add(self, prop):
        self._item.append(prop)

    def __getitem__(self, key):
        return self._item[key]

    def __len__(self):
        return len(self._item)
    
    def to_dataframe(self):
        # determining column names
        colnames = self._create_colnames(self._item[0])
        df = self._create_dataframe(colnames)

    def _create_colnames(self, df):
        type_list = (House, Garage, Advertiser, GeoCoordinates, Property)
        colnames = ['type']
        for key,value in self._item[0].__dict__.items():
            # import pdb; pdb.set_trace()
            if isinstance(value, type_list):
                namestr = key#str.lower(value.__class__.__name__)
                addstr = []
                for key1 in value.__dict__.keys():
                    addstr.append(namestr + '_' + key1)
            else:
                addstr = [key]
            colnames = colnames + addstr
        return colnames

    def _create_dataframe(self, attrs):
        df = pd.DataFrame()
        for item in self._item:
            tmp = {}
            for name in attrs:
                if name == 'type':
                    tmp[name] = [item.__class__.__name__]
                    continue
                try:
                    tmp[name] = [getattr(item,name)]
                except AttributeError:
                    atsplit = name.split('_', maxsplit=1)
                    obj = getattr(item, atsplit[0])
                    value = [getattr(obj, atsplit[1])]
                    if value == {}:
                        tmp[name] = None
                    else:
                        tmp[name] = value
            df = pd.concat([df, pd.DataFrame(tmp)])
        return df


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


class GeoCoordinates:
    def __init__(self, dct={}):
        self.north = dct.get('north', None)
        self.east = dct.get('east', None)


class ScrapeData:
    def __init__(self, dct={}):
        self.property_type = dct.get('property_type', '')
        self.city          = dct.get('city', '')
        self.sale_type     = dct.get('sale_type', '')
        # self.additional    = dct.get('additional', '')
    
    def create_query_url(self):
        pass

    def get_list_of_items_found(self):
        pass

    def query_search(self, url, header={}):
        r = requests.get(url, headers=header)
        if r.status_code == 200:
            return r
        else:
            print(f'There was a problem whith request. Status code is {r.status_code}')
            return None


class ScrapeDataIngatlan(ScrapeData):
    _url = 'https://ingatlan.com'
    _queryterm = 'szukites'
    _header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'Content-type': 'application/json',
                'Accept': '*/*',
                }
    
    def __init__(self, dct = {}):
        ScrapeData.__init__(self, dct=dct)
        self.property_type = dct.get('property_type', 'haz')
        self.sale_type     = dct.get('sale_type', 'elado')
        self.container     = PropertyContainer()
    
    def create_query_url(self):
        url = self._url + '/' + self._queryterm + '/' + self.sale_type + '+' + self.property_type + '+' + self.city.lower()
        return url

    def get_list_of_items_found(self):
        url_main = self.create_query_url()
        r = self.query_search(url_main, self._header)
        bs = BeautifulSoup(r.text)
        page_num = self._get_page_numbers(bs)
        # start to page the findings
        bslist = self._return_pages(url_main, page_num)
        bslist.append(bs)

    
    def _return_pages(self, url_main, page_num):
        pages = []
        for ii in tqdm(range(2, page_num+1)):
            url = url_main + f'?page={ii}'
            r = self.query_search(url, self._header)
            pages.append(BeautifulSoup(r.text, 'html.parser'))
        return pages

    def _get_page_numbers(self, bs):
        elem = bs.find('div', attrs={'class':'pagination__page-number'})
        # import pdb; pdb.set_trace()
        if elem == None:
            num = 1
        else:
            elem = elem.text.strip()
            num = int(re.findall(r'\d+', elem)[1])
        return num



if __name__ == "__main__":
    search_params = {'city': 'Szeged'}
    s = ScrapeDataIngatlan(dct=search_params)
    adv = Advertiser({'name': 'Balint Krisztian', 'phone': '06305655655', 'agency':'Ving'})
    coor = GeoCoordinates({'north':45, 'east':22})
    gdct = {
        'size'            : 25,
    }
    dct = {
        'size'            : 125,
        'url'             : 'www.google.com',
        'city'            : 'Szeged',
        'street'          : 'Fekete Sas utca',
        'price'           : 34000000,
        'price_ccy'       : 'HUF',
        'condition'       : 'kozepes allapotu',
        'construction_year' : 2000,
        'description'     : 'Blabal a akdfadf dfad adf ad sd sdsr er ncvnifvnsc v',
        'coordinates'     : coor,
        'unit_price'      : 230000,
        'unit_price_unit' : 'HUF',
        'advertiser'      : adv,
        'land_size'       : 586, 
        'room_number'     : 4, 
        'comfort'         : 'osszkomfort', 
        'energy_certificate' : 'A', 
        'stair_number'    : '1', 
        'heating'         : 'cirko', 
        'aircondition'    : 'nincs', 
        'bathroom'        : 'wcvel egyben', 
        'attic'           : 'beepitheto', 
        'cellar'          : 'nincs', 
        'parking'         : 'utcan es az udvarban', 
        'garage'          : Garage(dct=gdct)
    }
    h = House(dct)
    cont = PropertyContainer()
    for ii in range(5):
        cont.add(h)
