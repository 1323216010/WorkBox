import os
import pandas as pd
from tqdm import tqdm
import json

def find_files(path, include_list, exclude_list, file_types):
    result = []

    for root, dirs, files in os.walk(path):
        for file in files:
            # 检查文件名是否包含include_list中的任一字符串
            if any(substr in file for substr in include_list):
                # 检查文件名是否不包含exclude_list中的任一字符串
                if not any(substr in file for substr in exclude_list):
                    # 检查文件类型是否符合file_types中的任一类型
                    if any(file.endswith(ft) for ft in file_types):
                        result.append(os.path.join(root, file))
    return result

def filter_by_string(input_list, target_string):
    return [item for item in input_list if target_string in item]

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_csv(paths, data, path):
    stations = data['stations']
    barcode = data['barcode']
    # 创建一个外层的进度条对象
    outer_tqdm = tqdm(stations, desc='Overall Progress')
    for station in outer_tqdm:
        # 更新进度条的描述以反映当前的站点
        outer_tqdm.set_description(f"Generating data of {station}")

        # 得到当前站位的所有summary log路径
        filePaths = filter_by_string(paths, station)
        dfs = []

        flag = False
        # 内层循环，遍历站点的文件路径
        for filePath in filePaths:
            df = read_csv(filePath)
            if flag:
                try:
                    df = df[df[barcode] != '-']
                except:
                    continue
            else:
                flag = True
            dfs.append(df)

        # 合并数据并保存到CSV文件
        dfStation = pd.concat(dfs)
        dfStation.to_csv(f"{path}\\{station}_Data.csv", index=False)

def generate_csv_final(dfMerge, paths, data, path):
    stations = data['stations']
    barcode = data['barcode']
    SiteTime = data['SiteTime']

    dfMerge = filter_dataframe_by_criteria(dfMerge, {'bar_isFinalTest': True})
    # 创建一个外层的进度条对象
    outer_tqdm = tqdm(stations, desc='Overall Progress')
    for station in outer_tqdm:
        # 更新进度条的描述以反映当前的站点
        outer_tqdm.set_description(f"Generating data of {station}")

        # 得到当前站位的所有summary log路径
        filePaths = filter_by_string(paths, station)
        dfs = []

        flag = False
        # 内层循环，遍历站点的文件路径
        for filePath in filePaths:
            df = read_csv(filePath)
            if flag:
                try:
                    df = df[df[barcode] != '-']
                except:
                    continue
            else:
                flag = True
            dfs.append(df)

        # 合并数据并保存到CSV文件
        dfStation = pd.concat(dfs)

        # 创建一个用于过滤的条件
        condition = dfStation[[barcode , SiteTime]].merge(dfMerge, on=[barcode, SiteTime], how='inner').drop_duplicates()

        # 使用条件过滤dfStation
        filtered_df = dfStation[dfStation.set_index([barcode, SiteTime]).index.isin(condition.set_index([barcode, SiteTime]).index)].reset_index(drop=True)

        filtered_df.to_csv(f"{path}\\{station}_Data_Final.csv", index=False)

def excel_to_dict(file_path):
    # 使用pandas读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl', usecols=[0, 1], header=None)

    # 将前两列转换为字典
    result_dict = dict(zip(df[0], df[1]))

    return result_dict

def getDesc(list1, list2, data):
    paths = find_files('./faildesc', [data['machine']], [], ['xlsx'])
    if len(paths) == 0:
        return
    dict1 = excel_to_dict(paths[0])
    for index, value in enumerate(list1):
        if index <= 3:
            continue
        if value in dict1:
            list2[index] = dict1[value]
        else:
            print(value, 'can not be found in', paths[0])

def read_csv(path):
    col_names = pd.read_csv(path, nrows=1).columns
    df = pd.read_csv(path, usecols=col_names, low_memory=False, encoding="UTF-8", delimiter=',')
    return df

def filter_dataframe_by_criteria(df, criteria):
    """
    在DataFrame中查找所有符合给定条件的行。

    :param df: 要搜索的 pandas DataFrame。
    :param criteria: 一个字典，包含需要匹配的键值对。
    :return: 一个DataFrame，包含所有符合条件的行。
    """
    # 检查并处理重复的索引
    if not df.index.is_unique:
        df = df.reset_index(drop=True)

    # 使用 criteria 字典构建一个条件表达式
    condition = pd.Series([True] * len(df))
    for key, value in criteria.items():
        condition &= (df[key] == value)

    # 应用条件表达式并返回匹配的行
    return df[condition]

def save_list_as_json(data_list, filename):
    # 检查列表是否为空
    if data_list:
        # 列表非空，保存为 JSON 文件
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)
        print(f"The list of exception files has been saved to {filename}")
    else:
        # 列表为空
        pass

def version():
    print('Yield version is 20231205a')
    print("Update Log")
    print("=========================================")
    print("[2023-12-05]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Skip the exception files and save it as a json list")
    print("[2023-12-02]")
    print("-----------------------------------------")
    print("Fixes:")
    print("    - Reconstruct dfMerge with duplicate row index")
    print("[2023-12-01]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Allow type to be any string and add final data output")
    print("[2023-10-27]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Compatible with reading csv files with inconsistent line lengths")
    print("[2023-10-26]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Add failcode information")
    print("[2023-10-25]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Summarize the data for each station")
    print("[2023-10-24]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Add recursive logic to traverse subdirectories")
    print()
    print("For any questions or concerns, please contact:")
    print("Pengcheng.yan@cowellchina.com")
    print("=========================================")