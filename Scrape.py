import urllib3
from urllib.parse import urlencode
import certifi
import bs4

import sys, os, csv, time

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
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

if selenium.__version__ != '4.1.0':
    print('[ERROR] selenium version must be 4.1.0')
    exit()
   
options = Options()
options.headless = True
binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.binary = binary

def getPropertyData(p):
    url = p.find('a', class_='css-1y2bib4')['href']

    dateS = p.find('span', class_='css-1nj9ymt')
    date = '-'.join(dateS.string.split(' ')[-3:])

    priceP = p.find('p', class_='css-mgq8yx', attrs={'data-testid': 'listing-card-price'})
    price = -1
    i = 0
    for child in priceP.stripped_strings:
        price = child[1:].replace(',', '').strip()
        #Stop Powered by PM Price Finder
        if i == 0:
            break

    addressh2 = p.find('h2', class_='css-bqbbuf', attrs={'data-testid': 'address-wrapper'})
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

    features = p.find_all('span', class_='css-lvv8is', attrs={'data-testid': 'property-features-text-container'})
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
                if tempStr != 'Bed' and tempStr != 'Beds' and tempStr != 'Bath' and tempStr != 'Baths' and tempStr != 'Parking' and tempStr != '−':
                    prev = tempStr
                
                if tempStr == 'Bed' or tempStr == 'Beds' or tempStr == 'Bath' or tempStr == 'Baths' or tempStr == 'Parking':
                    if tempStr == 'Bed' or tempStr == 'Bath':
                        tempStr = tempStr.lower() + 's'
                    featuresDict[tempStr.lower()] = prev
                    prev = -1
                
                if 'm²' in tempStr:
                    #replace the commas in the land size so it doesn't stuff up the CSV files. 
                    featuresDict['land_size'] = tempStr[:-2].replace(',', '')
                    featuresDict['land_size_unit'] = tempStr.replace('m²', 'm2')[-2:]
    
    propType = p.find('span', class_='css-693528').string
    
    return (date, price, address, featuresDict, propType, url)

def isNoMatch(p):
    noMatchStr = p.find('h3', class_='css-1c8ubmt')
    if noMatchStr is None:
        return False
    if noMatchStr.string == "No exact matches":
        return True

def writeFile(filename, data):
    with open(filename, 'w') as f:
        #features: {'beds': -1, 'baths': -1, 'parking': -1, 'land_size': -1, 'land_size_unit': 'None'}
        f.write('"address","price","date","bedrooms","bathrooms","parking_spaces","land_size","land_size_unit","propertyType","url","houseFeatures","schoolsDistance","schoolsCount","salesHistory"\n')
        for d in data:
            #print(d.toString())
            f.write(d.toString() + '\n')

class Property:
    #def __init__(self, address, price, date, features, propType, extras, url):
    def __init__(self, address, price, date, features, propType, url):
        self.address = address
        self.price = price
        self.date = date
        self.features = features
        self.propType = propType
        #self.extras = extras
        self.url = url
        self.houseFeatures = []
        self.houseSchools = []
        self.salesHistory = []
    
    #address , price , date, bedrooms , bathrooms , parking_spaces , land_size , land_size_unit , extras
    #extras = swimmingpool, airconditioning, internallaundry, petsallowed, builtinwardrobes, gardencourtyard, study, gas, balconydeck
    def toString(self):
        retStr = f'{str(self.address)},{str(self.price)},{str(self.date)}'
        
        for k, v in self.features.items():
            retStr = retStr + f',{v}'

        #retStr = retStr + f',{self.propType},' + self.extras.replace(',', ';') + f',{self.url}'
        retStr = retStr + f',"{self.propType}","{self.url}"'
        retStr = retStr + f',{"-".join(self.houseFeatures)},{"-".join(self.houseSchools)},{len(self.houseSchools)},{"-".join(self.salesHistory)}'
        return retStr

    def getListingDetails(self):
        with webdriver.Firefox(options=options, executable_path=r'C:\BrowserDrivers\geckodriver.exe') as driver:
            driver.get(self.url)
            
            houseFeatures = []
            hasFeatures = True
            try:
                features = driver.find_elements(By.CSS_SELECTOR, 'li.css-vajaaq')
            except NoSuchElementException:
                #print("NO ELEMENT")
                hasFeatures = False
            except:
                #print("NO ELEMENT")
                hasFeatures = False

            if hasFeatures:
                houseFeatures = []
                for f in features:
                    if f.text == '':
                        continue
                    else:
                        houseFeatures.append(f'"{f.text}"')
            
            self.houseFeatures = houseFeatures

            houseSchools = []
            hasSchools = True
            try:
                schoolsButton = driver.find_element(By.CSS_SELECTOR, 'button.css-cq4evw').click()
            except NoSuchElementException:
                #print("NO ELEMENT")
                hasSchools = False
            except:
                #print("NO ELEMENT")
                hasSchools = False
            
            if hasSchools:
                houseSchools = []
                try:
                    schoolsList = driver.find_elements(By.CSS_SELECTOR, 'div.css-si4svp')
                except NoSuchElementException:
                    #print("NO ELEMENT")
                    hasSchools = False
                except:
                    #print("NO ELEMENT")
                    hasSchools = False
                
                for s in schoolsList:
                    houseSchools.append(s.text.split(' ')[0])
            
            self.houseSchools = houseSchools

    def getSalesHistory(self):
        with webdriver.Firefox(options=options, executable_path=r'C:\BrowserDrivers\geckodriver.exe') as driver:
            driver.get(f'https://www.domain.com.au/property-profile/{self.address}')
            
            #Weird properties, has no sales history or irelevant information like Listing - not sold, or (price unknown)
            #driver.get(f'https://www.domain.com.au/property-profile/12-keely-street-reservoir-vic-3073')
            #driver.get(f'https://www.domain.com.au/property-profile/24-development-boulevard-mill-park-vic-3082')
            #driver.get(f'https://www.domain.com.au/property-profile/35-delacombe-drive-mill-park-vic-3082')
            #driver.get(f'https://www.domain.com.au/property-profile/19-mayfield-drive-mill-park-vic-3082')
            
            salesHistory = []
            hasSalesHistory = True
            checkSalesHistory = 'Yes'
            try:
                checkSalesHistory = driver.find_element(By.CSS_SELECTOR, 'h5.css-mpkn6v')
            except NoSuchElementException:
                #print("NO CHECK SALES")
                hasSalesHistory = True
            except:
                #print("NO CHECK SALES")
                hasSalesHistory = True
            
            if checkSalesHistory == 'No history available':
                self.salesHistory = salesHistory
                return

            # Get more history button
            hasHistoryButton = True
            try:
                moreHistoryButton = driver.find_element(By.CSS_SELECTOR, 'button.css-e4xbky')
            except NoSuchElementException:
                #print("NO HISTORY BUTTON")
                hasHistoryButton = False
            except:
                #print("NO HISTORY BUTTON")
                hasHistoryButton = False
            
            if hasHistoryButton:
                moreHistoryButton.click()

            if hasSalesHistory:
                historyMonths, historyYears, historyPrice, historyType = [], [], [], []
                
                try:
                    historyMonths = driver.find_elements(By.CSS_SELECTOR, 'div.css-vajoca')
                    historyYears = driver.find_elements(By.CSS_SELECTOR, 'div.css-1qi20sy')

                    #historyPrice = driver.find_elements(By.CSS_SELECTOR, 'span.css-6xjfcu')
                    #Use this otherwise the price might be unknown
                    historyPrice = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="fe-co-property-timeline-card-heading"]')

                    #this does not include rented
                    #historyType = driver.find_elements(By.CSS_SELECTOR, 'div.css-jcs3kb')
                    historyType = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="fe-co-property-timeline-card-category"]')
                except NoSuchElementException: 
                    #print("NO HISTORY ELEMENTS")
                    print('')
                except:
                    print('')
                    #print("NO HISTORY ELEMENTS")
                
                if historyMonths != [] and historyYears != [] and historyPrice != [] and historyType != []:
                    #hpF = list(filter(lambda x: '$' in x.text, historyPrice))
                    
                    toRemoveAll = []
                    toRemovePrice = []
                    
                    for i in range(0, len(historyPrice)):
                        if historyPrice[i].text == 'Listed - not sold':
                            toRemovePrice.append(i)
                        
                        if historyPrice[i].text == '(price unknown)':
                            toRemovePrice.append(i)
                            toRemoveAll.append(i)

                    #https://www.geeksforgeeks.org/python-get-indices-of-true-values-in-a-binary-list/
                    #hpI = [i for i, x in enumerate(historyPrice) if '$' not in x.text]
                    #hpF = [x for i, x in enumerate(historyPrice) if i not in hpI]
                    #hmF = [x for i, x in enumerate(historyMonths) if i not in hpI]
                    #hyF = [x for i, x in enumerate(historyYears) if i not in hpI]
                    #htF = [x for i, x in enumerate(historyType) if i not in hpI]
                    
                    hpF = [x for i, x in enumerate(historyPrice) if i not in toRemovePrice]
                    hmF = [x for i, x in enumerate(historyMonths) if i not in toRemoveAll]
                    hyF = [x for i, x in enumerate(historyYears) if i not in toRemoveAll]
                    htF = [x for i, x in enumerate(historyType) if i not in toRemoveAll]

                    #turn historical price into an actual number
                    hpF2 = [h.text[1:] for h in hpF]
                    hpF3 = []
                    for hpf in hpF2:
                        if hpf[-1] == 'k':
                            hpF3.append(float(hpf[:-1])*(10**3))
                        elif hpf[-1] == 'm':
                            hpF3.append(float(hpf[:-1])*(10**6))
                        else:
                            hpF3.append(float(hpf[:-1])*(1))
                    
                    salesHistory = []
                    #for (hm, hy, hp, ht) in zip(hmF, hyF, hpF, htF):
                    for (hm, hy, hp, ht) in zip(hmF, hyF, hpF3, htF):
                        #salesHistory.append(f'{hm.text}={hy.text}={hp.text}={ht.text}')
                        #print(f'{hm.text}={hy.text}={hp.text}={ht.text}')
                        salesHistory.append(f'{hm.text.title()}/{hy.text}/{hp}/{ht.text}')
                        #print(f'{hm.text}/{hy.text.title()}={hp}={ht.text}')
                        #print(f'{hy.text}/{hm.text.title()}/{hp}/{ht.text}')
        
        self.salesHistory = salesHistory
                

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
#extras = "swimmingpool"

params = {
    #"bathrooms": 2,
    "excludepricewithheld": 1,
    #"carspaces": 2,
    "ssubs": 0
    #"features": extras
}

# Read suburbs.csv
if len(sys.argv) != 3:
    exit("usage: python Scrape.py folderName csvName.csv")

folderName = str(sys.argv[1])
os.makedirs(folderName)
csvName = str(sys.argv[2])

headers = []
content = []

with open(csvName) as csvData:
    csvReader = csv.reader(csvData)
    i = 0
    for row in csvReader:
        if i == 0:
            headers = row
            i += 1
        else:
            content.append(row)
            i += 1

#construct suburb URL
#only consider free standing?
queries = []
for sub, pcode, state in content:
    for i in range(1, 6, 1):
        #print(i)
        #print(sub.lower().replace(' ', '-') + '-vic-' + pcode + '/house/' + bedroomsUrl[i])
        queries.append(sub.lower().replace(' ', '-') + '-vic-' + pcode + '/house/' + bedroomsUrl[i])

sL = time.perf_counter()
for q in queries:
    sQ = time.perf_counter()
    props = []
    print(q)
    for i in range(1, 51, 1):
        params["page"] = i
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        #newURL = DOMAIN_SOLD_BASE + 'mill-park-vic-3082/' + 'house/' + bedroomsUrl[4] + '/?' + urlencode(params)
        newURL = DOMAIN_SOLD_BASE + q + '/?' + urlencode(params)
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
            #prop = Property(d[2], d[1], d[0], d[3], d[4], extras, d[5])
            prop = Property(d[2], d[1], d[0], d[3], d[4], d[5])
            prop.getListingDetails()
            prop.getSalesHistory()
            props.append(prop)
            #print(prop.toString())
    
    writeFile(folderName + '/' + q.replace('/house/', '-') + '.csv', props)
    eQ = time.perf_counter()
    print(q + ' time: ', (eQ - sQ))

eL = time.perf_counter()
print('total scrape time: ', (eL - sL))
