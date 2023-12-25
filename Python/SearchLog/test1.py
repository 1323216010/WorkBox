import pandas as pd
import json
from search1 import search_log_aps, search_log, search_data_aps
from utils import find_matching_list

config = 'C4050'

with open('config/' + config + '.json', 'r', encoding='utf-8') as file:
    files = json.load(file)

barcodes = []
for file in files:
    try:
        barcodes.append(find_matching_list(file, {'#PASS_FAIL': 'PASS'}))
    except:
        print(file)

with open(config + '_barcodes.json', 'w') as json_file:
    json.dump(barcodes, json_file)

with open('paths.json', 'r', encoding='utf-8') as file:
    list1 = json.load(file)

obj = [item for item in list1 if item["config"] == config][0]

dict0 = {}
dict0['FTU_path'] = obj['FTU']['path']
dict0['FTD_path'] = obj['FTD']['path']

with open(config + '_barcodes.json', 'r', encoding='utf-8') as file:
    barcodes = json.load(file)

for obj in barcodes:
    barcode = obj['barcode']
    if barcode == "":
        continue

    try:
        dict1 = {}
        dict1.update({'barcode': barcode})

        dict1.update(search_data_aps(obj['path'], {'barcode': barcode, '#PASS_FAIL': 'PASS'}))
        dict1.update(search_log(dict0['FTU_path'], {'barcode': barcode, 'PASS_FAIL': 'PASS'}))

        dict1.update(search_log(dict0['FTD_path'], {'barcode': barcode, 'PASS_FAIL': 'PASS'}, "FTD"))

        df = pd.DataFrame([dict1])

        df.to_csv('nvm_data.csv', index=False)
    except:
        print(barcode)


