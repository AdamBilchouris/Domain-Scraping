import os
import pandas as pd

READ_DIR = 'combinedFeaturesRemoved'
WRITE_DIR = 'combinedFeaturesRemoved'

header = ('"address","price","date","bedrooms","bathrooms","parking_spaces","land_size","land_size_unit","propertyType","url",'
          '"houseFeatures","schoolsDistance","schoolsCount","salesHistory","heating","air_con","internal_laundry","built_in_wardrobes",'
          '"secure_parking","study","close_to_shops","close_to_transport","close_to_schools","split_system","fully_fenced","solar_panels",'
          '"dishwasher","garage","alarm","garden","deck","balcony","pool","spa"')

bigDf = pd.DataFrame()
i = 0

for dirName, subdirList, fileList in os.walk(f'{READ_DIR}/'):
    for fname in fileList:
        filePath = f'{dirName}{fname}'
        if i == 0:
            bigDf = pd.read_csv(filePath)
        else:
            bigDf = bigDf.append(pd.read_csv(filePath))
        i += 1

bigDf.to_csv(f'{WRITE_DIR}/big.csv', index=False, header=header)