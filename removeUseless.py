import pandas as pd

READ_DIR = 'combinedFeaturesRemoved'
IFNAME = 'combinedFeaturesRemoved/big.csv'
OFNAME = 'combinedFeaturesRemoved/big_removed.csv'
bigDf = pd.read_csv(IFNAME)

features = ('"heating","air_con","internal_laundry","built_in_wardrobes",'
          '"secure_parking","study","close_to_shops","close_to_transport","close_to_schools","split_system","fully_fenced","solar_panels",'
          '"dishwasher","garage","alarm","garden","deck","balcony","pool","spa"')

sizeDf = bigDf.shape[0]
print('Before: ', sizeDf)
bigDf['houseFeatures'] = bigDf['houseFeatures'].astype(str).str.replace('"', '')
bigDf['houseFeatures'] = bigDf['houseFeatures'].str.replace('nan', '')
bigDf = bigDf[bigDf['houseFeatures'] != '']
sizeDf = bigDf.shape[0]
print('After: ', sizeDf)

for f in features.split(','):
    ff = f.strip('"')
    count = bigDf[bigDf[ff] == 0].shape[0]
    print(ff, count, sizeDf)
    if count > sizeDf / 2:
        del bigDf[ff]

print('Before: ', sizeDf)
print(bigDf['salesHistory'])
bigDf['salesHistory'] = bigDf['salesHistory'].astype(str).replace('nan', '')
bigDf = bigDf[bigDf['salesHistory'] != '']
bigDf = bigDf[bigDf['parking_spaces'].astype(int) != -1]
bigDf = bigDf[bigDf['schoolsCount'] > 0]
print(bigDf['salesHistory'])
sizeDf = bigDf.shape[0]
print('After: ', sizeDf)

bigDf.to_csv(OFNAME, index=False)
