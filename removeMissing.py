import os
import pandas as pd

READ_DIR = 'combinedFeatures'
WRITE_DIR = 'combinedFeaturesRemoved'

header = ('"address","price","date","bedrooms","bathrooms","parking_spaces","land_size","land_size_unit","propertyType","url",'
          '"houseFeatures","schoolsDistance","schoolsCount","salesHistory","heating","air_con","internal_laundry","built_in_wardrobes",'
          '"secure_parking","study","close_to_shops","close_to_transport","close_to_schools","split_system","fully_fenced","solar_panels",'
          '"dishwasher","garage","alarm","garden","deck","balcony","pool","spa"')

for dirName, subdirList, fileList in os.walk(f'{READ_DIR}/'):
    for fname in fileList:
        filePath = f'{dirName}{fname}'
        #if 'box-hill' in filePath:
        #    continue
        csv = pd.read_csv(filePath)
        print(filePath)
        # Remove properties if they have missing values
        csv = csv[csv['price'].astype(str).astype(int) >= 0]
        # Remove properties if they have missing values
        csv = csv[csv['bathrooms'] != -1]
        csv = csv[csv['parking_spaces'] != -1]
        csv = csv[csv['land_size'] != -1]
        csv.insert(1, 'suburb', ' '.join(fname[:-4].split('-')).title())
        #csv = csv.dropna()
        csv['houseFeatures'] = csv['houseFeatures'].astype(str).str.replace('"', '')
        csv['houseFeatures'] = csv['houseFeatures'].str.replace('nan', '')

        csv.to_csv(f'{WRITE_DIR}/{fname}', index=False, header=header)