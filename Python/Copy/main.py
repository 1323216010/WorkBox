import shutil
import os
import json
from utils import find_subdirs_with_keyword
from utils import find_files_with_progress
import shutil
import subprocess

def copy_files(json_file, destination_folder):
    # 确保目标文件夹存在
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 读取JSON文件中的路径列表
    with open(json_file, 'r', encoding='utf-8') as file:
        file_paths = json.load(file)

    # 遍历列表中的每个文件路径
    for path in file_paths:
        if os.path.isfile(path):
            # 构建目标文件路径
            file_name = os.path.basename(path)
            dest_path = os.path.join(destination_folder, file_name)

            # 在Windows系统中复制文件
            subprocess.run(f'copy "{path}" "{dest_path}"', shell=True)
        else:
            print(f"文件不存在或路径错误: {path}")

# 使用函数
json_file = 'D:\project\Python\CopyLog\C4050\paths\paths.json'  # JSON文件路径
destination_folder = 'D:\project\Python\CopyLog\C4050\datas'  # 目标文件夹路径
copy_files(json_file, destination_folder)

# def read_json_files(folder_path):
#     all_data = []
#
#     # 遍历文件夹中的所有文件
#     for filename in os.listdir(folder_path):
#         if filename.endswith('.json'):
#             file_path = os.path.join(folder_path, filename)
#
#             # 读取JSON文件内容
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 data = json.load(file)
#                 if isinstance(data, list):
#                     all_data.extend(data)  # 假设文件内容是列表
#
#     return all_data
#
#
# def write_json_file(data, output_file):
#     with open(output_file, 'w', encoding='utf-8') as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)
#
#
# # 使用函数
# folder_path = r'D:\project\Python\CopyLog\c4051module\paths'  # 这里填写你的文件夹路径
# output_file = r'D:\project\Python\CopyLog\c4051module\paths\paths.json'  # 输出文件的路径和文件名
# combined_data = read_json_files(folder_path)
# write_json_file(combined_data, output_file)

# files = []

# path = input("请输入搜索路径: ")
# paths = find_subdirs_with_keyword(path, "PD31013-L")
# paths = []
# # 打开文件并读取 JSON 数据
# with open('path_list.json', 'r', encoding='utf-8') as file:
#     paths = json.load(file)
#

# for path in paths:
#     list1 = find_files_with_progress(path, ["APS_OQC", "ApsCalibrationSweepFromMcu"], [], [".csv"], depth=None, match_all_includes=True)
#     files.extend(list1)
#     with open(path.split("\\")[-1] + '.json', 'w') as file:
#         json.dump(list1, file)
#
# with open('paths.json', 'w') as file:
#     json.dump(files, file)

# with open('paths.json', 'r', encoding='utf-8') as file:
#     files = json.load(file)
#
# # 目标目录
# destination_directory = 'D:\project\Python\CopyLog\datas'
#
# for file in files:
#     if os.path.isfile(file):
#         # 复制每个文件到目标目录
#         shutil.copy(file, destination_directory)
#     else:
#         print(f"File not found: {file}")