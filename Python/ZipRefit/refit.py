import zipfile
import os
import csv
from io import StringIO
import configparser
import json
from utils import ensure_dir
from utils import find_substring_in_list
from utils import replace_iguana

def combine_ini_content(ini_content):
    config = configparser.ConfigParser()
    config.read_string(ini_content)  # 使用 read_string 而不是 read

    # 初始化列表，用于存储合并后的内容
    headers = []
    uppers = []
    lowers = []
    contents = []

    # 遍历所有 section 并合并数据
    for section in config.sections():
        headers += config.get(section, 'Header').split(',')
        uppers += config.get(section, 'Uppers').split(',')
        lowers += config.get(section, 'Lowers').split(',')
        contents += config.get(section, 'Contents').split(',')

    # 将每个列表合并为一个字符串，并用换行符分隔
    combined_string = '\n'.join([','.join(headers), ','.join(uppers), ','.join(lowers), ','.join(contents)])

    return combined_string

def ensure_testitem_column(csv_content, item):
    reader = csv.reader(StringIO(csv_content))
    rows = list(reader)

    if len(rows) < 4 or '#TESTITEM' in rows[0]:
        return csv_content, False  # 如果文件行数不足或者已经包含#TESTITEM列，则无需修改

    # 在第一列前添加#TESTITEM列
    for i in range(len(rows)):
        if i == 0:
            rows[i].insert(0, '#TESTITEM')  # 第一行添加列标题
        elif 1 <= i <= 2:
            rows[i].insert(0, '-')  # 第二行和第三行添加'-'
        else:
            rows[i].insert(0, item)  # 第四行及之后添加item值

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    return output.getvalue(), True

def remove_duplicate_columns(csv_content):
    reader = csv.reader(StringIO(csv_content))
    rows = list(reader)

    if not rows:
        return csv_content, False

    # 检测并移除重复列
    header = rows[0]
    unique_cols = []
    indices_to_keep = []
    for i, col in enumerate(header):
        if col not in unique_cols:
            unique_cols.append(col)
            indices_to_keep.append(i)

    if len(indices_to_keep) == len(header):
        return csv_content, False  # 没有重复列

    new_rows = []
    for row in rows:
        new_row = [row[i] for i in indices_to_keep]
        new_rows.append(new_row)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(new_rows)
    return output.getvalue(), True

def process_zip_file(zip_file_path, output_folder_path):
    file_name = os.path.basename(zip_file_path)
    file_name = replace_iguana(file_name)
    csv_file_name = os.path.splitext(file_name)[0] + '.csv'
    new_zip_file_name = 'VR_' + file_name if not file_name.startswith('VR_') else file_name
    new_csv_file_name = 'VR_' + csv_file_name if not csv_file_name.startswith('VR_') else csv_file_name
    new_zip_path = os.path.join(output_folder_path, new_zip_file_name)
    needs_processing = not file_name.startswith('VR_')
    csv_modified = False
    ini_content = None
    exisit_csv_json = False

    with zipfile.ZipFile(zip_file_path, 'r') as zip_read:
        with zipfile.ZipFile(new_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if 'legend_metadata.json' in item.filename:
                    # 读取并解析 JSON 文件
                    legend_metadata_content = json.loads(zip_read.read(item.filename).decode('utf-8'))
                    if not legend_metadata_content['station_info']['station_type']:
                        # 修改 JSON 文件中的特定字段
                        legend_metadata_content['station_info']['station_type'] = find_substring_in_list(file_name)
                        # 将修改后的 JSON 内容写入新的 ZIP 文件
                        zip_write.writestr(item.filename, json.dumps(legend_metadata_content, indent=4))
                        needs_processing = True
                        exisit_csv_json = True
                    break
            for item in zip_read.infolist():
                if item.filename.lower().endswith('.ini'):
                    needs_processing = True
                    ini_content = combine_ini_content(zip_read.read(item.filename).decode('utf-8'))
                    break
            for item in zip_read.infolist():
                if 'legend_metadata.json' in item.filename:
                    continue
                if item.filename.lower().endswith('.ini'):
                    continue  # 删除ini文件
                if replace_iguana(item.filename) == csv_file_name:
                    exisit_csv_json = True
                    csv_content = zip_read.read(item.filename).decode('utf-8')
                    # 检查并添加#TESTITEM列
                    csv_content, testitem_added = ensure_testitem_column(csv_content, find_substring_in_list(item.filename))
                    # 检查并移除重复列
                    csv_content, duplicates_removed = remove_duplicate_columns(csv_content)
                    # 比较ini内容和csv内容，添加缺失的列
                    if ini_content:
                        csv_content, ini_columns_added = add_missing_columns_from_ini(csv_content, ini_content)
                        csv_modified = csv_modified or ini_columns_added
                    csv_modified = testitem_added or duplicates_removed or csv_modified
                    needs_processing = needs_processing or csv_modified
                    if needs_processing:
                        zip_write.writestr(new_csv_file_name, csv_content)
                    continue
                if needs_processing:
                    data = zip_read.read(item.filename)
                    zip_write.writestr(item, data)

    if not needs_processing or not exisit_csv_json:
        print(file_name)
        os.remove(new_zip_path)

def add_missing_columns_from_ini(csv_content, ini_content):
    csv_reader = csv.reader(StringIO(csv_content))
    ini_reader = csv.reader(StringIO(ini_content))

    csv_rows = list(csv_reader)
    ini_rows = list(ini_reader)

    csv_headers = csv_rows[0]
    ini_headers = ini_rows[0]

    # Find missing columns in CSV that are present in INI
    missing_columns = [col for col in ini_headers if col not in csv_headers]

    if not missing_columns:
        return csv_content, False  # No missing columns

    # Add missing columns to CSV
    for col in missing_columns:
        col_index = ini_headers.index(col)  # Get the index of the missing column from INI
        for i in range(len(csv_rows)):
            if i == 0:
                csv_rows[i].append(col)  # Add header
            else:
                # Add the corresponding value from the INI file if it exists, otherwise add an empty string
                value = ini_rows[i][col_index] if i < len(ini_rows) else ''
                csv_rows[i].append(value)

    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerows(csv_rows)
    return output.getvalue(), True

def process_zip_files_in_folder(source_folder_path, output_folder_path):
    ensure_dir(output_folder_path)
    for file_name in os.listdir(source_folder_path):
        if file_name.endswith('.zip'):
            old_zip_path = os.path.join(source_folder_path, file_name)
            try:
                process_zip_file(old_zip_path, output_folder_path)
            except:
                print('error file:', old_zip_path)

def refit_iguana_ftud(source_folder_path, output_folder_path):
    ensure_dir(output_folder_path)
    process_zip_files_in_folder(source_folder_path, output_folder_path)
