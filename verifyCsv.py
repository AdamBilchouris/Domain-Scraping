import os
import sys
import pandas as pd

#https://www.pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
i = 0
totalProperties = 0
hasNoneDir = 'selectionClean'
for dirName, subdirList, fileList in os.walk(f'{hasNoneDir}/'):
    for fname in fileList:
        filePath = f'{dirName}/{fname}'
        csv = pd.read_csv(filePath)
        print(f'{filePath} : {csv.shape}')
        i = i + 1
        totalProperties = totalProperties + csv.shape[0]

print(f'Total suburbs = {i//5}')
print(f'Total properties = {totalProperties}')
