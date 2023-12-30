import os
import csv
from tqdm import tqdm

def find_subdirs_with_keyword(directory, keyword):
    """
    在给定目录的一级子目录中搜索包含关键字的子目录。

    :param directory: 文件夹的绝对路径
    :param keyword: 要搜索的关键字
    :return: 包含关键字的一级子目录列表
    """
    matching_subdirs = []

    # 确保提供的路径是目录
    if not os.path.isdir(directory):
        return matching_subdirs

    # 遍历一级子目录
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and keyword in item:
            matching_subdirs.append(item_path)

    return matching_subdirs

def find_files_with_progress(path, include_list, exclude_list, file_types, depth=None, match_all_includes=False):
    result = []
    path_depth = len(path.rstrip(os.sep).split(os.sep))  # 获取初始路径的深度

    # 获取目录下所有文件的总数，用于进度条的最大值
    total_files = sum([len(files) for r, d, files in os.walk(path)])

    with tqdm(total=total_files, desc="Searching Files") as pbar:
        for root, dirs, files in os.walk(path):
            # 计算当前遍历的深度
            current_depth = len(root.rstrip(os.sep).split(os.sep))
            # 如果设置了深度，且当前深度超过初始路径深度加上设置的深度，则跳过
            if depth is not None and (current_depth - path_depth) >= depth:
                del dirs[:]  # 清空dirs列表，防止继续向下遍历
                continue

            for file in files:
                # 根据match_all_includes的值选择检查方式
                if match_all_includes:
                    # 检查文件名是否包含include_list中的所有字符串
                    if all(substr in file for substr in include_list):
                        if not any(substr in file for substr in exclude_list):
                            if any(file.endswith(ft) for ft in file_types):
                                result.append(os.path.join(root, file))
                else:
                    # 检查文件名是否包含include_list中的任一字符串
                    if any(substr in file for substr in include_list):
                        if not any(substr in file for substr in exclude_list):
                            if any(file.endswith(ft) for ft in file_types):
                                result.append(os.path.join(root, file))
                # 更新进度条
                pbar.update(1)

    return result

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
            # 根据match_all_includes的值选择检查方式
            if match_all_includes:
                # 检查文件名是否包含include_list中的所有字符串
                if all(substr in file for substr in include_list):
                    if not any(substr in file for substr in exclude_list):
                        if any(file.endswith(ft) for ft in file_types):
                            result.append(os.path.join(root, file))
            else:
                # 检查文件名是否包含include_list中的任一字符串
                if any(substr in file for substr in include_list):
                    if not any(substr in file for substr in exclude_list):
                        if any(file.endswith(ft) for ft in file_types):
                            result.append(os.path.join(root, file))
    return result

def find_matching_records(csv_file, criteria):
    """
    读取CSV文件，返回所有符合给定条件的行。

    :param csv_file: CSV文件的路径。
    :param criteria: 一个字典，包含需要匹配的键值对。
    :return: 符合条件的行的列表。
    """
    matching_rows = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if all(row.get(key) == value for key, value in criteria.items()):
                matching_rows.append(row)

    return matching_rows

def find_records(csv_file, field_name):
    """
    读取CSV文件，返回一个字典，该字典包含指定字段名和对应的值。

    :param csv_file: CSV文件的路径。
    :param field_name: 需要提取值的字段名称。
    :return: 包含指定字段名和对应值的字典。
    """
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # 读取第二行，即数据行
        row = next(reader, None)
        if row and field_name in row:
            return {field_name: row[field_name]}
        else:
            return {field_name: None}  # 如果没有找到字段或者没有数据行，返回None

