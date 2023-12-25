import pandas as pd
from search import search_log_aps
from search import search_log

dict1 = {}
barcode = input("请输入要查找的barcode: ")
dict1.update({'barcode': barcode})

path = input("请输入APS搜索路径: ")
dict1.update(search_log_aps(path, {'barcode': barcode, '#PASS_FAIL': 'PASS'}))
# Global_time_stamp = input("请输入要查找的APS Global_time_stamp: ")
# dict1.update(get_aps(path, {'barcode': barcode, '#PASS_FAIL': 'PASS', 'Global_time_stamp': Global_time_stamp}))

# path = input("请输入FTU搜索路径: ")
dict1.update(search_log(path, {'barcode': barcode, 'PASS_FAIL': 'PASS'}))

# path = input("请输入FTD搜索路径: ")
dict1.update(search_log(path, {'barcode': barcode, 'PASS_FAIL': 'PASS'}, "FTD"))

# 将字典转换为 DataFrame
df = pd.DataFrame([dict1])

df.to_csv('nvm_data.csv', index=False)
