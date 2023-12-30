import os
import json
import numpy as np
import csv
import pandas as pd
from compute import get_NVMdefect_64byte_Page_Type, get_NVMdefect_64byte_Page_Type_IN, get_NVMdefect_64byte_Page_Type_PDX, focusGains_OCLHV_1p0_Comp, rfpn_correction, focusGains_OCL_Comp
from nvm_pit import dp_correct_pit
from nvm_varo import dp_correct_varo
from nvm_pdx import dp_correct_pdx
from nvm_in import dp_correct_in

def correct(IDraw , dict1, file_name):
    if dict1.get("program", "").lower() == "in":
        nvm_data = get_NVMdefect_64byte_Page_Type_IN(file_name, get_data(dict1['nvm_data_path']))
    elif dict1.get("program", "").lower() == "pdx":
        nvm_data = get_NVMdefect_64byte_Page_Type_PDX(file_name, get_data(dict1['nvm_data_path']))
    else:
        nvm_data = get_NVMdefect_64byte_Page_Type(file_name, get_data(dict1['nvm_data_path']))

    if dict1.get("program", "").lower() == "pit":
        IDraw = IDraw[40:, :]
        return dp_correct_pit(IDraw, nvm_data, dict1, file_name)
    if dict1.get("program", "").lower() == "varo":
        if dict1.get("lightingMode", "dark").lower() == 'd50':
            IDraw = focusGains_OCLHV_1p0_Comp(IDraw, {'focusGain': {}})
        else:
            IDraw = np.squeeze(rfpn_correction(IDraw))
        return dp_correct_varo(IDraw, nvm_data, dict1, file_name)
    if dict1.get("program", "").lower() == "pdx":
        return dp_correct_pdx(IDraw, nvm_data, dict1, file_name)
    if dict1.get("program", "").lower() == "in":
        if dict1.get("lightingMode", "dark").lower() == 'd50':
            IDraw = focusGains_OCL_Comp(IDraw)
        return dp_correct_in(IDraw, nvm_data, dict1, file_name)
    print('NVM Data decoding did not specify the project type; defaulting to PIT decoding')
    return dp_correct_pit(IDraw, nvm_data, dict1, file_name)

def read_raw_image(file_path, width):
    with open(file_path, 'rb') as file:
        img = file.read()
        img_array = np.frombuffer(img, dtype=np.uint16)  # 使用 16 位深度
        print('height*width =', img_array.size)

        # 创建一个可写的副本
        img_array = img_array.copy()
        img_array = img_array.reshape((int(img_array.size/width), width))
        return img_array

def save_range_to_csv(array, row_start, row_end, col_start, col_end, filename):
    """
    将指定范围的二维ndarray数据保存到CSV文件中，并在文件中包含行和列的起始索引信息。
    数据中包含行索引和列索引。

    :param array: 二维ndarray。
    :param row_start: 起始行索引。
    :param row_end: 结束行索引。
    :param col_start: 起始列索引。
    :param col_end: 结束列索引。
    :param filename: 保存的CSV文件名。
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # 写入行和列的起始索引信息
        writer.writerow(['Row Start Index', 'Row End Index', 'Column Start Index', 'Column End Index'])
        writer.writerow([row_start, row_end, col_start, col_end])

        # 空行作为分隔
        writer.writerow([])

        # 写入列索引
        col_indices = [''] + list(range(col_start, col_end + 1))  # 额外添加一个空元素作为左上角的空白
        writer.writerow(col_indices)

        # 写入数据和行索引
        for i, row in enumerate(array[row_start:row_end + 1]):
            writer.writerow([i + row_start] + list(row[col_start:col_end + 1]))

def find_files(path, include_list, exclude_list, file_types, depth=None, match_all_includes=False):
    result = []
    path_depth = len(path.rstrip(os.sep).split(os.sep))  # 获取初始路径的深度

    for root, dirs, files in os.walk(path):
        # 计算当前遍历的深度
        current_depth = len(root.rstrip(os.sep).split(os.sep))
        # 如果设置了深度，且当前深度超过初始路径深度加上设置的深度，则跳过
        if depth is not None and (current_depth - path_depth) >= depth:
            del dirs[:]  # 清空dirs列表，防止继续向下遍历
            continue

        for file in files:
            # 如果include_list为空，则跳过包含检查
            include_check = (not include_list) or (all(substr in file for substr in include_list) if match_all_includes else any(substr in file for substr in include_list))
            exclude_check = not any(substr in file for substr in exclude_list)
            type_check = any(file.endswith(ft) for ft in file_types)

            if include_check and exclude_check and type_check:
                result.append(os.path.join(root, file))

    return result

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def find_bounding_box(locations, d):
    # 初始化坐标边界值
    x1 = y1 = float('inf')
    x2 = y2 = float('-inf')

    # 遍历所有点，更新边界值
    for point in locations:
        x, y = point
        x1 = min(x1, x)
        y1 = min(y1, y)
        x2 = max(x2, x)
        y2 = max(y2, y)

    # 返回边界坐标
    return x1-d, x2+d, y1-d, y2+d

def get_data(path):
    # 检查文件扩展名
    if path.endswith('.csv'):
        # 尝试不同的编码格式读取CSV文件
        encodings = ['utf-8', 'ISO-8859-1', 'GBK', 'utf-16']
        for encoding in encodings:
            try:
                data = pd.read_csv(path, encoding=encoding)
                list1 = [data.columns.tolist()]
                list1.extend(data.values.tolist())
                return list1
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("Failed to read the CSV file with the tried encodings.")
    elif path.endswith(('.xls', '.xlsx')):
        # 读取Excel文件
        data = pd.read_excel(path)
        list1 = [data.columns.tolist()]
        list1.extend(data.values.tolist())
        return list1
    else:
        raise ValueError("The file format is not supported. Please provide a CSV or Excel file.")

    return []
def get_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        dict1 = json.load(f)

    return dict1

def print_version():
    print('DPCDeltaMap version is 20231230a')
    print("=========================================")
    print("Update Log")
    print("=========================================")
    print("[2023-12-30]")
    print("-----------------------------------------")
    print("Fixes:")
    print("    - Compensate image based on FPC compensation for IN D50.")
    print("[2023-12-27]")
    print("-----------------------------------------")
    print("Fixes:")
    print("    - In Varo D50 mode, the image is compensated based on the average of 4 nearby Gr/Gb values.")
    print("    - In Varo Dark mode, the image is subjected to row FPN correction and OBP cropping.")
    print("[2023-12-26]")
    print("-----------------------------------------")
    print("Fixes:")
    print("    - The program, mode, and lightingMode in the configuration are no longer case-sensitive.")
    print("    - Implement the focusGains_OCLHV_1p0_Comp algorithm for image preprocessing in the Varo project.")
    print("Features:")
    print("    - Add nvm decoding of Varo, PDX, IN.")
    print("    - Add the option to output raw data or not.")
    print("[2023-12-20]")
    print("-----------------------------------------")
    print("Fixes:")
    print("    - Apply NVM data for image data correction.")
    print("Features:")
    print("    - Save coordinates when nvm data is applied.")
    print("[2023-12-18]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Implement a cropping feature to remove the first 40 rows from images in the PIT program.")
    print("[2023-12-14]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Introduce sensor size configuration options to accommodate various project requirements.")
    print("[2023-12-12]")
    print("-----------------------------------------")
    print("Features:")
    print("    - Add horizontal and vertical coordinates display to DeltaMap.")
    print("    - Discontinue the generation of JSON files.")
    print()
    print("For any questions or concerns, please contact:")
    print("Pengcheng.yan@cowellchina.com")
    print("=========================================")