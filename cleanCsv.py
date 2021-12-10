from numpy import NaN
import pandas as pd
import os

READ_DIR = 'selection'
WRITE_DIR = 'selectionClean'
for dirName, subdirList, fileList in os.walk(f'{READ_DIR}/'):
    for fname in fileList:
        filePath = f'{dirName}/{fname}'
        #filePath = f'selection/airport-west-vic-3042-2-bedrooms.csv'
        if fname == 'selection.csv':
            continue
        print(f'{fname}')
        csv = pd.read_csv(filePath)
        csv['propertyType'] = csv['propertyType'].str.replace('"', '')
        csv['houseFeatures'] = csv['houseFeatures'].astype(str).str.replace('"', '')
        csv['houseFeatures'] = csv['houseFeatures'].str.replace('nan', '')
        csv.to_csv(f'{WRITE_DIR}/{fname}', index=False)
        
        #change the header to have quotes again
        with open(f'{WRITE_DIR}/{fname}', 'r') as f:
            content = f.readlines()
        content[0] = ','.join([f'"{f}"' for f in content[0].strip().split(',')]) + '\n'
        with open(f'{WRITE_DIR}/{fname}', 'w') as f:
            f.writelines(content)
