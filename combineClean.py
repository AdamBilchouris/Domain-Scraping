import os
import pandas as pd

READ_DIR = 'selectionClean'
WRITE_DIR = 'selectionCleanCombined'

filePaths = []

for dirName, subdirList, fileList in os.walk(f'{READ_DIR}/'):
    for fname in fileList:
        filePaths.append(f'{dirName}{fname}')

header = '"address","price","date","bedrooms","bathrooms","parking_spaces","land_size","land_size_unit","propertyType","url","houseFeatures","schoolsDistance","schoolsCount","salesHistory"'

content = []
i = 0
totalProperties = 0

for fp in filePaths:
    with open(f'{fp}', 'r') as f:
        if i == 0:
            csv = pd.read_csv(fp)
        else:
            csv2 = pd.read_csv(fp)
            csv = csv.append(csv2)
        i += 1

    if fp.find('5-bedrooms') > 0:
        posSlash = fp.find('/')
        posDash = fp.find('-vic')
        suburb = fp[posSlash:posDash]
        print(suburb, csv.shape)
        totalProperties += csv.shape[0]

        #change the header to have quotes again
        csv.to_csv(f'{WRITE_DIR}{suburb}.csv', index=False)
        with open(f'{WRITE_DIR}{suburb}.csv', 'r') as f:
            content = f.readlines()
        content[0] = ','.join([f'"{f}"' for f in content[0].strip().split(',')]) + '\n'
        with open(f'{WRITE_DIR}{suburb}.csv', 'w') as f:
            f.writelines(content)
        i = 0

print(f'Total Properties = {totalProperties}')

