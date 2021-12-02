import selenium
import urllib3
from urllib.parse import urlencode
import certifi
import bs4
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

if urllib3.__version__ != '1.26.7':
    print('[ERROR] urllib3 version must be 1.26.7')
    exit()

if bs4.__version__ != '4.10.0':
    print('[ERROR] beautifulsoup4 version must be 4.10.0')
    exit()

if certifi.__version__ != '2021.10.08':
    print('[ERROR] urllib3 version must be 1.26.7')
    exit()

options = Options()
options.headless = True
binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.binary = binary

def getPropertyData(p):
    url = p.find('a', class_='css-1y2bib4')['href']

    dateS = p.find('span', class_='css-1nj9ymt')
    date = '-'.join(dateS.string.split(' ')[-3:])

    priceP = p.find('p', class_='css-mgq8yx')
    price = -1
    for child in priceP.stripped_strings:
        price = child[1:].replace(',', '').strip()

    addressh2 = p.find('h2', class_='css-bqbbuf')
    address = ''
    aIter = 0
    for a in addressh2.children:
        for aa in a.stripped_strings:
            #fixes a weird bug:
            #('30-Sep-2014', '553000', '.css-iqrvhs{max-width:100%;text-overflow:ellipsis;white-space:nowrap;overflow:hidden;}-19-mayfield-drive-mill-park-vic-3082', {'beds': '.css-9fxapx{position:absolute;width:1px;height:1px;margin:-1px;padding:0;-webkit-clip:rect(1px,1px,1px,1px);clip:rect(1px,1px,1px,1px);border:0;overflow:hidden;-webkit-clip-path:inset(100%);clip-path:inset(100%);-webkit-clip-path:none;}', 'baths': '2', 'parking': '2'}, 'House')
            if aa == ',' or '.css' in aa:
                continue

            # The case when we have the suburb, state, and postcode.
            # Make sure the strings follow the property-profile naming convention.
            # For example, https://www.domain.com.au/property-profile/8-brabham-drive-mill-park-vic-3082
            if aIter > 0:
                addressPart = aa.lower().replace(' ', '-')
                address = address + '-' + addressPart

            else:
                addressPart = aa.lower().split()
                address = address + '-'.join(addressPart)

            aIter = aIter + 1

    address = address.strip()

    features = p.find_all('span', class_='css-lvv8is')
    prev = -1
    featuresDict = {'beds': -1, 'baths': -1, 'parking': -1, 'land_size': -1, 'land_size_unit': 'None'}
    for f in features:
        for ff in f.children:
            temp = ff.string.split()
            #fixed a weird bug,
            #('30-Sep-2014', '553000', '19-mayfield-drive-mill-park-vic-3082', {'beds': '.css-9fxapx{position:absolute;width:1px;height:1px;margin:-1px;padding:0;-webkit-clip:rect(1px,1px,1px,1px);clip:rect(1px,1px,1px,1px);border:0;overflow:hidden;-webkit-clip-path:inset(100%);clip-path:inset(100%);-webkit-clip-path:none;}', 'baths': '2', 'parking': '2'}, 'House')
            if len(temp) < 1 or '.css' in ''.join(temp):
                continue
            else:
                tempStr = ''.join(temp)
                if tempStr != 'Beds' and tempStr != 'Baths' and tempStr != 'Parking':
                    prev = tempStr
                
                if tempStr == 'Beds' or tempStr == 'Baths' or tempStr == 'Parking':
                    featuresDict[tempStr.lower()] = prev
                    prev = -1
                
                if 'm²' in tempStr:
                    featuresDict['land_size'] = tempStr[:-2]
                    featuresDict['land_size_unit'] = tempStr.replace('m²', 'm2')[-2:]
    
    propType = p.find('span', class_='css-693528').string
    
    return (date, price, address, featuresDict, propType, url)

def isNoMatch(p):
    noMatchStr = p.find('h3', class_='css-1c8ubmt')
    if noMatchStr is None:
        return False
    if noMatchStr.string == "No exact matches":
        return True

class Property:
    def __init__(self, address, price, date, features, propType, extras, url):
        self.address = address
        self.price = price
        self.date = date
        self.features = features
        self.propType = propType
        self.extras = extras
        self.url = url
        #This will need to be changed based on your file paths.
        #self.driver = webdriver.Firefox(options = options, executable_path=r'C:\BrowserDrivers\Chromium\chromedriver.exe')
    
    #address , price , date, bedrooms , bathrooms , parking_spaces , land_size , land_size_unit , extras
    #extras = swimmingpool, airconditioning, internallaundry, petsallowed, builtinwardrobes, gardencourtyard, study, gas, balconydeck
    def toString(self):
        retStr = f'{str(self.address)},{str(self.price)},{str(self.date)}'
        
        for k, v in self.features.items():
            retStr = retStr + f',{v}'

        retStr = retStr + f',{self.propType},' + self.extras.replace(',', ';') + f',{self.url}'
        
        return retStr

    def getListingDetails(self):
        with webdriver.Firefox(options=options, executable_path=r'C:\BrowserDrivers\geckodriver.exe') as driver:
            driver.get(self.url)
            
            houseFeatures = []
            hasFeatures = True
            try:
                features = driver.find_elements(By.CSS_SELECTOR, 'li.css-vajaaq')
            except NoSuchElementException:
                print("NO ELEMENT")
                hasFeatures = False
            except:
                print("NO ELEMENT")
                hasFeatures = False

            if hasFeatures:
                for f in features:
                    if f.text == '':
                        continue
                    else:
                        houseFeatures.append(f.text)
            
            print(houseFeatures)
            houseSchools = []
            hasSchools = True
            try:
                schoolsButton = driver.find_element(By.CSS_SELECTOR, 'button.css-cq4evw').click()
            except NoSuchElementException:
                print("NO ELEMENT")
                hasSchools = False
            except:
                print("NO ELEMENT")
                hasSchools = False
            
            if hasSchools:
                try:
                    schoolsList = driver.find_elements(By.CSS_SELECTOR, 'div.css-si4svp')
                except NoSuchElementException:
                    print("NO ELEMENT")
                    hasSchools = False
                except:
                    print("NO ELEMENT")
                    hasSchools = False
                
                for s in schoolsList:
                    houseSchools.append(float(s.text.split(' ')[0]))
            
            print(houseSchools)


#1 bedroom, 2,3,4 bedrooms, 5+ bedrooms.
bedroomsUrl = {1: '1-bedroom', 2: '2-bedrooms',
               3: '3-bedrooms', 4: '4-bedrooms', 5: '5-bedrooms'}

#example:
#https://www.domain.com.au/sold-listings/mill-park-3082/
DOMAIN_SOLD_BASE = 'https://www.domain.com.au/sold-listings/'

# 4 bedroom houses in mill park vic 3082, with 2 bathrooms and parking spaces, and a pool:
#DOMAIN_TEST_LINK = https://www.domain.com.au/sold-listings/mill-park-vic-3082/house/3-bedrooms/?excludepricewithheld=1&ssubs=0&features=swimmingpool
"""
The "features" parameter can take multiple values. Separate them by a comma, i.e.,
"features": "swimmingpool,airconditioningm,internallaundry"
"""

# Keep incrementing the current page until no more matches are found.
# Page 50 seems to be the maximum.
currPage = 1
extras = "swimmingpool"

params = {
    "bathrooms": 2,
    "excludepricewithheld": 1,
    "carspaces": 2,
    "ssubs": 0,
    "features": extras
}

for i in range(1, 51, 1):
    params["page"] = i
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    newURL = DOMAIN_SOLD_BASE + 'mill-park-vic-3082/' + 'house/' + bedroomsUrl[4] + '/?' + urlencode(params)
    res = http.request('GET', newURL, fields=params)
    soup = bs4.BeautifulSoup(res.data, 'html.parser')
    
    
    if isNoMatch(soup):
        print(f'Blank Page {i}')
        break

    print(f'Page {i}')
    properties = soup.find_all('li', class_='css-1qp9106')
    for p in properties:
        d = getPropertyData(p)
        #print(d)
        prop = Property(d[2], d[1], d[0], d[3], d[4], extras, d[5])
        print(prop.toString())
        prop.getListingDetails()