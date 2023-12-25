import json
from utils import find_files_with_list

with open('paths.json', 'r', encoding='utf-8') as file:
    list1 = json.load(file)

list2 = list1[0]['APS']['path']
result = find_files_with_list(list2, ["_Tester_"], ["LimitLog"], [".csv"])
print()