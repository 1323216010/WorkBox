import os
import json
from datetime import datetime

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

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

def extract_substring(s):
    # 检查空格或"VR"的位置
    end = s.find(' ') if ' ' in s else s.find('VR')
    # 如果都不存在，则截取到字符串末尾
    end = end if end != -1 else len(s)
    # 返回第二个字符到截止位置的子串，限制最多14个字符
    return s[1:end][:14]

def get_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        dict1 = json.load(f)

    return dict1

def convert_datetime_format(datetime_str):
    # 检查是否已经是目标格式
    try:
        # 尝试按目标格式解析
        datetime.strptime(datetime_str, '%Y_%m_%d_%H:%M:%S:%f')
        # 如果解析成功，则格式已经是目标格式
        return datetime_str
    except ValueError:
        # 如果解析失败，则尝试按原始格式解析
        try:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S:%f')
            # 按目标格式格式化并限制毫秒为三位数
            formatted_str = dt.strftime('%Y_%m_%d_%H:%M:%S:%f')
            return formatted_str[:-3]  # 移除最后三位，保留毫秒
        except ValueError:
            # 如果原始格式也无法解析，则返回错误信息
            return "Invalid format"

def insert(df, dict0):
    df.insert(0, '#TESTITEM', ['-', '-', 'Gopher'])
    df.insert(0, 'LOT_ID', ['-', '-', df.at[2, 'lotNum']])
    df.insert(0, 'Program_Ver', ['-', '-', df.at[2, 'Test_SW_ver']])
    df.insert(0, 'Config', ['-', '-', dict0['config']])
    df.insert(0, 'program_name', ['-', '-', 'Varo_sensor'])
    df.insert(0, 'Socket_Index', ['-', '-', df.at[2, 'Site'][-1]])
    df.insert(0, 'Serial_Number', ['-', '-', df.at[2, 'sensorID']])