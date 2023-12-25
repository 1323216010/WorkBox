import json
import os
from search1 import search_log, search_data_aps
from utils import ensure_dir, delete_file_if_exists
import pandas as pd


with open('config.json', 'r', encoding='utf-8') as file:
    configs = json.load(file)

config = configs['config']

with open('paths.json', 'r', encoding='utf-8') as file:
    list1 = json.load(file)

obj_path = [item for item in list1 if item["config"] == config][0]

with open(config + '_barcodes.json', 'r', encoding='utf-8') as file:
    barcodes = json.load(file)

ensure_dir('./datas/'+ config)
station_data = {}
delete_file_if_exists(config + '.txt')
for list1 in barcodes:
    for obj in list1:
        barcode = obj['barcode']
        if barcode == "":
            continue

        try:
            dict1 = {}
            dict1.update({'barcode': barcode})

            dict1.update(search_data_aps(obj['path'], {configs['aps_barcode']: barcode, '#PASS_FAIL': 'PASS'}))
            dict1.update(search_log(station_data, obj_path['FTU']['path'], {configs['FTU_barcode']: barcode, 'PASS_FAIL': 'PASS'}))

            dict1.update(search_log(station_data, obj_path['FTD']['path'], {configs['FTD_barcode']: barcode, 'PASS_FAIL': 'PASS'}, "FTD"))

            df = pd.DataFrame([dict1])

            df.to_csv('./datas/' + config + '/' + barcode + '.csv', index=False)
        except:
            print(barcode)
            with open(config + '.txt', 'a') as file:
                file.write(barcode + '\n')

os.system("pause")