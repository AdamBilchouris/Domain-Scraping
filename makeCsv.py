import os
import json
import csv
import numpy as np
import pandas as pd
from pandas.core.indexes.base import Index

# read the json files from 'selection' folder
READ_DIR = 'selectionMedian'
WRITE_DIR = 'outMedian'

try:
    os.remove(f'{WRITE_DIR}/big.csv')
except:
    print('no big.csv')

#header = ('"2012","2013","2014","2015","2016","2017","2018","2019","2020",'
#          '"2021-01","2021-02","2021-03","2021-04","2021-05","2021-06","2021-07","2021-08","2021-09","2021-10",'
#          '"2020-11"')

jsonHeader = ('"2012-12-31","2013-12-31","2014-12-31","2015-12-31","2016-12-31","2017-12-31","2018-12-31","2019-12-31","2020-12-31",'
          '"2021-01-31","2021-02-28","2021-03-31","2021-04-30","2021-05-31","2021-06-30","2021-07-31","2021-08-31","2021-09-30","2021-10-31",'
          '"2020-11-30"')

jsonHeader2 = '"2021/2012","2021/2013","2021/2014","2021/2015","2021/2016","2021/2017","2021/2018","2021/2019","2021/2020"'
jsonHeader3 = ('"2021-10/2021-09","2021-10/2021-08","2021-10/2021-07","2021-10/2021-06","2021-10/2021-05","2021-10/2021-04","2021-10/2021-03","2021-10/2021-02","2021-10/2021-01",'
             '"2021-09/2021-08","2021-09/2021-07","2021-09/2021-06","2021-09/2021-05","2021-09/2021-04","2021-09/2021-03","2021-09/2021-02","2021-09/2021-01",'
             '"2021-08/2021-07","2021-08/2021-06","2021-08/2021-05","2021-08/2021-04","2021-08/2021-03","2021-08/2021-02","2021-08/2021-01",'
             '"2021-07/2021-06","2021-07/2021-05","2021-07/2021-04","2021-07/2021-03","2021-07/2021-02","2021-07/2021-01",'
             '"2021-06/2021-05","2021-06/2021-04","2021-06/2021-03","2021-06/2021-02","2021-06/2021-01",'
             '"2021-05/2021-04","2021-05/2021-03","2021-05/2021-02","2021-05/2021-01",'
             '"2021-04/2021-03","2021-04/2021-02","2021-04/2021-01",'
             '"2021-03/2021-02","2021-03/2021-01",'
             '"2021-02/2021-01"')

header = f'"suburb",{jsonHeader},{jsonHeader2},{jsonHeader3}'

def appendDays(s):
    if '-02' in s:
        return '-28'
    if s[4:] in ('-01', '-03', '-05', '-07', '-08', '-10', '-12'):
        return '-31'
    if s[4:] in ('-04', '-06', '-09', '-11'):
        return '-30'


for f in os.listdir(READ_DIR):
    ff = open(f'selection/{f}', 'r')
    jsonData = json.load(ff)
    
    csvData = []
    medians2021 = []
    
    suburb = '-'.join(f.split('-')[:-1])
    csvData.append(' '.join(suburb.split('-')[:-1]))

    for jh in jsonHeader.split(','):
        jhS = jh.strip('"')
        if jhS in jsonData:
            if '2021' in jhS:
                medians2021.append(int(jsonData[jhS]['price']))
            csvData.append(str(jsonData[jhS]['price']))
        else:
            csvData.append('-1')
    median2021 = np.median(medians2021).astype(int)
        
    for jh in jsonHeader2.split(','):
        jhS = jh.strip('"').split('/')[1]
        jhS += '-12-31'
        if jhS in jsonData:
            medYear = jsonData[jhS]['price']
            ratio = median2021 / medYear
            csvData.append(str(ratio))
        else:
            csvData.append('0')
    
    for jh in jsonHeader3.split(','):
        jhS = jh.strip('"').split('/')
        jh1, jh2 = jhS[0] + appendDays(jhS[0]), jhS[1] + appendDays(jhS[1])
        
        if jh1 in jsonData and jh2 in jsonData:
            medMonth1 = jsonData[jh1]['price']
            medMonth2 = jsonData[jh2]['price']
            ratio = medMonth1 / medMonth2
            csvData.append(str(ratio))
        else:
            csvData.append('0')

    with open(f'{WRITE_DIR}/{suburb}.csv', 'w') as out:
        out.write(f'{header}\n')
        out.write(f'{",".join(csvData)}')

i = 0
#pandas sucks
"""
for f in os.listdir(WRITE_DIR):
    if i == 0:
        csv = pd.read_csv(f'{WRITE_DIR}/{f}')
    else:
        csvTemp = pd.read_csv(f'{WRITE_DIR}/{f}')
        csv = csv.append(csvTemp)
    i += 1
csv.to_csv(f'{WRITE_DIR}/big.csv', header=header, index=False)
""" 

header = []
csvData = []
for f in os.listdir(WRITE_DIR):
    with open(f'{WRITE_DIR}/{f}', 'r') as ff:
        csvF = csv.reader(ff)
        i = 0
        for c in csvF:
            if i == 0:
                header = c
            else:
                csvData.append(c)
            i += 1

with open(f'{WRITE_DIR}/big.csv', 'w') as out:
    out.write('"' + '","'.join(header) + '"\n')
    for c in csvData:
        out.write(f'{",".join(c)}\n')
