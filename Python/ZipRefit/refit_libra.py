import zipfile
import os
import csv
from io import StringIO
from utils import ensure_dir
from utils import find_substring_in_list
from utils import replace_second_occurrence

def ensure_testitem_column(csv_content, item):
    reader = csv.reader(StringIO(csv_content))
    rows = list(reader)

    if 'Site' in rows[0]:
        site_index = rows[0].index('Site')
        site = rows[3][site_index][-1]
    else:
        site = 'Z'

    if 'build_num' in rows[0]:
        build_num_index = rows[0].index('build_num')
        rows[3][build_num_index] = 'C4.0'

    sensorid_index = rows[0].index('SensorID')

    if 'SensorID_I2C' in rows[0]:
        sensorid_i2c_index = rows[0].index('SensorID_I2C')
        rows[3][sensorid_i2c_index] = rows[3][sensorid_index]

    if 'station' in rows[0]:
        station = rows[0].index('station')
        for i in range(len(rows)):
            del rows[i][station]
    if 'PrismHolderSN' in rows[0]:
        PrismHolderSN = rows[0].index('PrismHolderSN')
        for i in range(len(rows)):
            del rows[i][PrismHolderSN]
    if 'LensSN' in rows[0]:
        LensSN = rows[0].index('LensSN')
        for i in range(len(rows)):
            del rows[i][LensSN]

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    return output.getvalue(), True, site

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
    machine = find_substring_in_list(file_name)
    csv_file_name = os.path.splitext(file_name)[0] + '.csv'
    new_zip_file_name = 'VR_' + file_name if not file_name.startswith('VR_') else file_name
    new_csv_file_name = 'VR_' + csv_file_name if not csv_file_name.startswith('VR_') else csv_file_name
    new_zip_path = os.path.join(output_folder_path, new_zip_file_name)
    needs_processing = not file_name.startswith('VR_')
    csv_modified = False

    with zipfile.ZipFile(zip_file_path, 'r') as zip_read:
        with zipfile.ZipFile(new_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if item.filename == csv_file_name:
                    csv_content = zip_read.read(item.filename).decode('utf-8')
                    # 检查并添加#TESTITEM列
                    csv_content, testitem_added, site = ensure_testitem_column(csv_content, find_substring_in_list(item.filename))
                    # 检查并移除重复列
                    csv_content, duplicates_removed = remove_duplicate_columns(csv_content)
                    csv_modified = testitem_added or duplicates_removed
                    needs_processing = needs_processing or csv_modified
                    if needs_processing:
                        new_csv_file_name = replace_second_occurrence(new_csv_file_name, machine, site)
                        zip_write.writestr(new_csv_file_name, csv_content)
                    continue
                if needs_processing:
                    data = zip_read.read(item.filename)
                    zip_write.writestr(item, data)

    if site:
        old_zip_path = os.path.join(output_folder_path, new_zip_file_name)
        new_zip_file_name = replace_second_occurrence(new_zip_file_name, machine, site)
        new_zip_path = os.path.join(output_folder_path, new_zip_file_name)
        if os.path.exists(old_zip_path):
            os.rename(old_zip_path, new_zip_path)

    if not needs_processing:
        os.remove(new_zip_path)

def process_zip_files_in_folder(source_folder_path, output_folder_path):
    ensure_dir(output_folder_path)
    for file_name in os.listdir(source_folder_path):
        if file_name.endswith('.zip'):
            old_zip_path = os.path.join(source_folder_path, file_name)
            try:
                process_zip_file(old_zip_path, output_folder_path)
            except:
                print('error file:', old_zip_path)

source_folder_path = r'C:\Users\pengcheng.yan\Desktop\legend\Libra'
output_folder_path = r'C:\Users\pengcheng.yan\Desktop\legend\Libra\output'
ensure_dir(output_folder_path)
process_zip_files_in_folder(source_folder_path, output_folder_path)
