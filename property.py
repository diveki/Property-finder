import pandas as pd
import os
import numpy as np
from bs4 import BeautifulSoup
import requests
import urllib
import re
import tqdm
import time
import pickle
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By



print('Reloaded')

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

class Flat(Property):
    def __init__(self, dct={}):
        Property.__init__(self, dct=dct)


class Advertiser:
    def __init__(self, dct={}):
        self.name   = dct.get('name', None)
        self.phone  = dct.get('phone', None)
        self.agency = dct.get('agency', None)

    def __str__(self):
        return '{name=' + str(self.name) + ' phone=' + str(self.phone) + ' agency=' + str(self.agency) + '}'

    def __repr__(self):
        return f'{self.__class__.__name__}(name=' + str(self.name) + ' phone=' + str(self.phone) + ' agency=' + str(self.agency) + ')'


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

    def __str__(self):
        return '{north=' + str(self.north) + ' east=' + str(self.east) + '}'

    def __repr__(self):
        return f'{self.__class__.__name__}(north=' + str(self.north) + ', east=' + str(self.east) + ')'


class ScrapeData:
    def __init__(self, dct={}):
        self.property_type = dct.get('property_type', '')
        self.city          = dct.get('city', '')
        self.sale_type     = dct.get('sale_type', '')
        self._driver       = False
        # self.additional    = dct.get('additional', '')

    def create_query_url(self):
        pass

    def get_list_of_items_found(self):
        pass

    def query_search(self, url, header={}):
        time.sleep(5)
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

    def get_url_list_of_items_found(self):
        url_main = self.create_query_url()
        r = self.query_search(url_main, self._header)
        bs = BeautifulSoup(r.text, 'html.parser')
        self._page_num = self._get_page_numbers(bs)
        # start to page the findings
        self._bslist = self._return_pages(url_main, self._page_num)
        self._bslist.append(bs)
        # get details from theresults
        url_list = []
        for item in self._bslist:
            url_list.append(self._find_item_url(item))
        # import pdb; pdb.set_trace()
        url_list = [self._url + ext for ls in url_list for ext in ls]
        return url_list

    def get_target_pages(self, url_list):
        bs = []
        for url in tqdm.tqdm(url_list):
            r = self.query_search(url, self._header)
            bs.append(BeautifulSoup(r.text, 'html.parser'))
        return bs

    def initialize_property_class(self):
        if self.property_type in ['haz', 'house']:
            return House
        elif self.property_type in ['lakas', 'flat']:
            return Flat
        elif self.property_type in ['garazs', 'garage']:
            return Garage
        else:
            raise TypeError('`self.property_type` has a wrong definition!!')

    def get_properties(self):
        urlslist = self.get_url_list_of_items_found()
        pages = self.get_target_pages(urlslist)
        prop_class = self.initialize_property_class()
        for ii in tqdm.tqdm(range(len(urlslist))):
            # import pdb; pdb.set_trace()
            features = self.populate_property(urlslist[ii], pages[ii])
            prop = prop_class(features)
            self.container.add(prop)

    def populate_property(self, url, page):
        dct = {}
        dct = self._populate_url(dct, url)
        dct = self._populate_city(dct, self.city)
        dct = self._populate_price(dct, page)
        dct = self._populate_size(dct, page)
        dct = self._populate_land_size(dct, page)
        dct = self._populate_room_number(dct, page)
        dct = self._populate_condition(dct, page)
        dct = self._populate_construction_year(dct, page)
        dct = self._populate_comfort(dct, page)
        dct = self._populate_energy_certificate(dct, page)
        dct = self._populate_stair_number(dct, page)
        dct = self._populate_heating(dct, page)
        dct = self._populate_aircondition(dct, page)
        dct = self._populate_bathroom(dct, page)
        dct = self._populate_view(dct, page)
        dct = self._populate_attic(dct, page)
        dct = self._populate_cellar(dct, page)
        dct = self._populate_parking(dct, page)
        dct = self._populate_description(dct, page)
        dct = self._populate_coordinates(dct, url)
        dct = self._populate_unit_price(dct)
        dct = self._populate_advertiser(dct, url)
        return dct

    def _populate_url(self, dct, url):
        dct['url'] = url
        return dct

    def _populate_city(self, dct, city):
        dct['city'] = city
        return dct

    def _populate_price(self, dct, bs):
        unit_conversion = {'ezer': 1000., 'millió':1000000.}
        elem = self._get_page_element(bs, 'div', attrs={'class':'parameter parameter-price'})
        pr = self._get_page_element(elem, 'span', attrs={'class':'parameter-value'})
        price = pr.text.split()
        dct['price'] = float(price[0].replace(',','.')) * unit_conversion[price[1]]
        dct['price_ccy'] = price[2]
        return dct

    def _populate_size(self, dct, bs):
        elem = self._get_page_element(bs, 'div', attrs={'class':'parameter parameter-area-size'})
        pr = self._get_page_element(elem, 'span', attrs={'class':'parameter-value'})
        size = pr.text.split()[0]
        dct['size'] = float(size)
        return dct

    def _populate_land_size(self, dct, bs):
        elem = self._get_page_element(bs, 'div', attrs={'class':'parameter parameter-lot-size'})
        pr = self._get_page_element(elem, 'span', attrs={'class':'parameter-value'})
        size = pr.text.split()[0]
        dct['land_size'] = float(size)
        return dct

    def _populate_room_number(self, dct, bs):
        elem = self._get_page_element(bs, 'div', attrs={'class':'parameter parameter-room'})
        pr = self._get_page_element(elem, 'span', attrs={'class':'parameter-value'})
        size = pr.text
        dct['room_number'] = size
        return dct

    def _populate_condition(self, dct, bs):
        keyword = 'Ingatlan állapota'
        elem = self._get_page_element(bs, 'div', attrs={'class':'paramterers'})
        tds = elem.find_all('td')
        tdtext = [td.text for td in tds]
        try:
            ind = tdtext.index(keyword)
            dct['condition'] = tdtext[ind+1]
        except:
            pass
        return dct

    def _populate_construction_year(self, dct, bs):
        keyword = 'Építés éve'
        elem = self._get_page_element(bs, 'div', attrs={'class':'paramterers'})
        tds = elem.find_all('td')
        tdtext = [td.text for td in tds]
        try:
            ind = tdtext.index(keyword)
            dct['construction_year'] = tdtext[ind+1]
        except:
            pass
        return dct

    def _populate_comfort(self, dct, bs):
        keyword = 'Komfort'
        try:
            value = self._get_td_element(bs,keyword)
            dct['comfort'] = value
        except:
            pass
        return dct

    def _populate_energy_certificate(self, dct, bs):
        keyword = 'Energiatanúsítvány'
        try:
            value = self._get_td_element(bs,keyword)
            dct['energy_certificate'] = value
        except:
            pass
        return dct

    def _populate_stair_number(self, dct, bs):
        keyword = 'Épület szintjei'
        try:
            value = self._get_td_element(bs,keyword)
            dct['stair_number'] = value
        except:
            pass
        return dct

    def _populate_heating(self, dct, bs):
        keyword = 'Fűtés'
        try:
            value = self._get_td_element(bs,keyword)
            dct['heating'] = value
        except:
            pass
        return dct

    def _populate_aircondition(self, dct, bs):
        keyword = 'Légkondicionáló'
        try:
            value = self._get_td_element(bs,keyword)
            dct['aircondition'] = value
        except:
            pass
        return dct

    def _populate_bathroom(self, dct, bs):
        keyword = 'Fürdő és WC'
        try:
            value = self._get_td_element(bs,keyword)
            dct['bathroom'] = value
        except:
            pass
        return dct

    def _populate_view(self, dct, bs):
        keyword = 'Kilátás'
        try:
            value = self._get_td_element(bs,keyword)
            dct['view'] = value
        except:
            pass
        return dct

    def _populate_attic(self, dct, bs):
        keyword = 'Tetőtér'
        try:
            value = self._get_td_element(bs,keyword)
            dct['attic'] = value
        except:
            pass
        return dct

    def _populate_cellar(self, dct, bs):
        keyword = 'Pince'
        try:
            value = self._get_td_element(bs,keyword)
            dct['cellar'] = value
        except:
            pass
        return dct

    def _populate_parking(self, dct, bs):
        keyword = 'Parkolás'
        try:
            value = self._get_td_element(bs,keyword)
            dct['parking'] = value
        except:
            pass
        return dct

    def _populate_description(self, dct, bs):
        try:
            elem = self._get_page_element(bs, 'div', attrs={'class':'long-description'})
            dct['description'] = elem.text
        except:
            pass
        return dct

    def _populate_coordinates(self, dct, url):
        if not self._driver:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.
            self._driver = webdriver.Chrome(options=chrome_options)
        self._driver.get(url)
        element = self._driver.find_element_by_class_name('map-holder')
        self._driver.execute_script("arguments[0].scrollIntoView();", element)
        # import pdb; pdb.set_trace()
        element = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, "details-map")))
        try:
            bs = BeautifulSoup(self._driver.page_source, 'html.parser')
            openmap = bs.find('div', attrs={'id':'details-map'})
            crd = openmap['data-bbox']
            crd = self._get_coordinates_from_text(crd)
        except:
            print(f'`{url}` has some issues to provide coordinates!')
        # elem = self._get_page_element(bs, 'div', attrs={'id':'details-map'})
        dct['coordinates'] = crd
        return dct

    def _populate_unit_price(self, dct):
        try:
            pr = dct['price']
            sz = dct['size']
            ccy = dct['price_ccy']
            dct['unit_price'] = pr / sz
            dct['unit_price_unit'] = ccy
        except KeyError as e:
            dct['unit_price'] = None
            dct['unit_price_unit'] = None
        return dct

    def _populate_advertiser(self, dct, url):
        if not self._driver:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.
            self._driver = webdriver.Chrome(options=chrome_options)
        self._driver.get(url)
        try:
            element = self._driver.find_element_by_class_name('phone-number')
            but = element.find_element_by_tag_name('button')
            but.click()
        except:
            print('Could not click on phone number')
        try:
            bs = BeautifulSoup(self._driver.page_source, 'html.parser')
            phone = bs.find('a', attrs={'class':'number phone-number-holder phone-number-visible'}).text
            name = self._get_agent_name(bs)
            agency = self._get_agency(bs)
            ag = {'name':name, 'phone':phone, 'agency':agency}
            ag = Advertiser(dct=ag)
        except:
            print(f'`{url}` has some issues to provide advertiser details!')
        # # elem = self._get_page_element(bs, 'div', attrs={'id':'details-map'})
        dct['advertiser'] = ag
        return dct

    def _get_agent_name(self, bs):
        elem = bs.find('div', attrs={'class':'agent-name'})
        if elem:
            return elem.text
        else:
            return None

    def _get_agency(self, bs):
        elem = bs.find('span', attrs={'class':'office-name'})
        if elem:
            return elem.text
        else:
            return None

    def _get_coordinates_from_text(self,text):
        t = text.split(',')
        N = int(len(t) / 2)
        coor = []
        for ii in range(N):
            tmp = GeoCoordinates({'north':float(t[2*ii+1]), 'east':float(t[2*ii])})
            coor.append(tmp)
        return coor

    def _get_td_element(self, bs, keyword):
        elem = self._get_page_element(bs, 'div', attrs={'class':'paramterers'})
        tds = elem.find_all('td')
        tdtext = [td.text for td in tds]
        ind = tdtext.index(keyword)
        value = tdtext[ind+1]
        return value

    def _get_page_element(self, bs, tag_name, attrs={}):
        elem = bs.find(tag_name, attrs=attrs)
        return elem

    def _find_item_url(self, item):
        bs = item.find_all('a',attrs={'class':['listing__thumbnail', 'js-listing-active-area']})
        url = []
        for i in range(0, len(bs),2):
            url = url + [bs[i]['href']]
        return url

    def _return_pages(self, url_main, page_num):
        pages = []
        for ii in range(2,3):#tqdm.tqdm(range(2, page_num+1)):
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

def load_data():
    f=open('target_urls.pkl', 'rb')
    urls = pickle.load(f)
    f.close()
    f=open('target_pages.pkl', 'rb')
    bs = pickle.load(f)
    f.close()
    return (urls, bs)


if __name__ == "__main__":
    search_params = {'city': 'Szeged'}
    s = ScrapeDataIngatlan(dct=search_params)
    import pickle
    urls, bs = load_data()

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
