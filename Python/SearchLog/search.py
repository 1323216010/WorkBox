import os
import json
import pandas as pd
from utils import find_files
from utils import find_matching_records
from utils import filter_dataframe_by_criteria
from utils import find_records
from utils import merge_csv_files

def search_log_aps(path, criteria):
    files = find_files(path, ["_Tester_"], ["LimitLog"], [".csv"])
    dict1 = {}
    for file in files:
        print(file)
        if file.endswith('.csv'):
            list = find_matching_records(file, criteria)
            if len(list) != 0:
                dict1 = list[0]
                # 获取文件所在目录
                file_dir = os.path.dirname(file)
                # 拼接新的路径
                dict1['summary_path'] = file
                dict1['debug_path'] = os.path.join(file_dir,
                                                   "Debug_" + dict1['Site'][-1] + "\\" + dict1["time"].replace("_", ""))
                break

    print(dict1['debug_path'])

    dict2 = {}

    # 打开文件并读取 JSON 数据
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 过滤掉 obj["station"] 不等于 "APS" 的元素
    data = [obj for obj in data if obj["station"] == "APS"]

    # 遍历列表中的每个对象
    for obj in data:
        if not obj["feature"] == "_Tester_":
            # 找到数据保存路径
            files = find_files(dict1['debug_path'], [obj["feature"]], ["LimitLog"], [".csv"])
            # 获取数据的值
            dict2[obj["name1"]] = find_records(files[0], obj["name2"])[obj["name2"]]
        else:
            listDict = find_matching_records(dict1['summary_path'], criteria)
            # 获取数据的值
            dict2[obj["name1"]] = listDict[0][obj["name2"]]

    return dict2

def search_log(path, criteria, station="FTU", global_time_stamp="global_time_stamp"):
    # 打开文件并读取 JSON 数据
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 过滤掉 obj["station"] 不等于 "APS" 的元素
    data = [obj for obj in data if obj["station"] == station]

    dict2 = {}
    # 遍历列表中的每个对象
    for obj in data:
        # 找到数据保存路径
        files = find_files(path, [station, obj["feature"]], ["LimitLog"], [".csv"], depth=None, match_all_includes=True)
        df = merge_csv_files(files)
        df = filter_dataframe_by_criteria(df, criteria)

        if criteria.get(global_time_stamp) is None:
            # 注意：如果有多行符合条件，这里只会转换第一行
            row_dict = df.iloc[0].to_dict()

            # 获取global_time_stamp
            criteria[global_time_stamp] = row_dict[global_time_stamp]
        else:
            # 注意：如果有多行符合条件，这里只会转换第一行
            row_dict = df.iloc[0].to_dict()

        dict2[obj["name1"]] = row_dict[obj["name2"]]

    return dict2
