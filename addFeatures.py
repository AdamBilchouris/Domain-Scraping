import os
import pandas as pd


READ_DIR = 'selectionCleanCombined'
#READ_DIR = 'testFeatures'
WRITE_DIR = 'combinedFeatures'

filePaths = []

for dirName, subdirList, fileList in os.walk(f'{READ_DIR}/'):
    for fname in fileList:
        filePaths.append(f'{dirName}{fname}')

features = ['heating', 'air con', 'internal laundry', 'built in wardrobes', 'secure parking', 'study', 'close to shops', 'close to transport',
            'close to schools', 'split system', 'fully fenced', 'solar panels', 'dishwasher', 'garage', 'alarm', 'garden',
            'deck', 'balcony', 'pool', 'spa']

featuresDict = {'heating': 0, 'air con': 0, 'internal laundry': 0, 'built in wardrobes': 0, 'secure parking': 0, 'study': 0, 'close to shops': 0,
                'close to transport': 0, 'close to schools': 0, 'split system': 0, 'fully fenced': 0, 'solar panels': 0, 'dishwasher': 0, 'garage': 0,
                'alarm': 0, 'split system': 0, 'garden': 0, 'deck': 0, 'balcony': 0, 'pool': 0, 'spa': 0}


header = '"address","price","date","bedrooms","bathrooms","parking_spaces","land_size","land_size_unit","propertyType","url","houseFeatures","schoolsDistance","schoolsCount","salesHistory"'

for f in features:
    header += f',"{f.replace(" ", "_")}"'

for fp in filePaths:
    print(fp)
    with open(f'{fp}', 'r') as f:
        csv = pd.read_csv(fp)
        i = 14
        for ff in features:
            csv.insert(i, str(ff).replace(' ', '_'), 0)
            i += 1
        
        for i in csv.index:
            #houseFeatures = featuresDict.copy()
            csv.at[i, 'houseFeatures'] = str(csv.at[i, 'houseFeatures']).replace('nan', '')
            hf = str(csv.loc[i]['houseFeatures']).lower()

            for ff in features:
                if ff in hf:
                    csv.at[i, str(ff).replace(' ', '_')] = 1
                else:
                    csv.at[i, str(ff).replace(' ', '_')] = 0
                    #csv.insert(i, str(ff).replace(' ', '_'), 1)
                    #houseFeatures[ff] = 1
            csv.at[i, 'houseFeatures'] = str(csv.at[i, 'houseFeatures']).replace('nan', '')
            csv.at[i, 'salesHistory'] = str(csv.at[i, 'salesHistory']).replace('nan', '')
        
        posSlash = fp.find('/')
        posDash = fp.find('.csv')
        fname = fp[posSlash:posDash]

        csv.to_csv(f'{WRITE_DIR}/{fname}.csv', index=False)

        #change the header to have quotes again
        content = []
        with open(f'{WRITE_DIR}/{fname}.csv', 'r') as f:
            content = f.readlines()
        content[0] = header + '\n'
        with open(f'{WRITE_DIR}/{fname}.csv', 'w') as f:
            f.writelines(content)
            
print(header)