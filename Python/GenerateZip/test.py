import os
import pandas as pd
import shutil
from utils import ensure_dir, find_files, extract_substring
import zipfile

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def zip_copy_directory(src, dst, ziph, exclude_dir=None):
    for root, dirs, files in os.walk(src):
        if exclude_dir and os.path.basename(root) == exclude_dir:
            continue  # 跳过exclude_dir指定的目录
        for file in files:
            file_path = os.path.join(root, file)
            # 修改文件的保存路径，使其包含在dst指定的目录中
            rel_dir = os.path.relpath(root, src)
            if rel_dir == exclude_dir:  # 如果是排除目录下的文件，直接放在dst目录下
                dst_path = os.path.join(dst, file)
            else:
                dst_path = os.path.join(dst, rel_dir, file)
            ziph.write(file_path, dst_path)

if __name__ == '__main__':
    source_folder_path = r'C:\Users\pengcheng.yan\Desktop\legend\Gopher\OriginalData'
    output_folder_path = r'C:\Users\pengcheng.yan\Desktop\legend\Gopher\out'
    ensure_dir(output_folder_path)

    paths = find_files(source_folder_path, ['Gopher_Tester'], ['LimitLog'], ['.csv'])

    for path in paths:
        file_name = os.path.basename(path)
        data = pd.read_csv(path, header=None, dtype=str)
        data = data.dropna(axis=1, how='all')
        headers = data.iloc[0].tolist()
        upper_limit = data.iloc[1].tolist()
        lower_limit = data.iloc[2].tolist()

        total = 0
        dict1 = {}
        for index, row in data.iloc[3:].iterrows():
            result_data = pd.DataFrame([upper_limit, lower_limit, row.tolist()], columns=headers)

            global_time_stamp = result_data.loc[2, 'global_time_stamp']
            site = result_data.loc[2, 'Site'][-1]
            time = extract_substring(global_time_stamp)
            debug_path = os.path.join(os.path.dirname(path), 'Debug_' + site, time)

            barcode = result_data.loc[2, 'sensorID']
            site_time = result_data.loc[2, 'SiteTime']
            dict1['name'] = 'VR_C4051_Gopher_' + site + '_' + barcode + '_' + site_time

            pass_fail_index = next((i for i, v in enumerate(row) if v in ['PASS', 'FAIL']), None)
            if pass_fail_index is not None:
                for col in headers[pass_fail_index + 1:]:
                    if not is_number(result_data.loc[2, col]):
                        result_data.drop(col, axis=1, inplace=True)

            # 创建zip文件
            zip_file_path = os.path.join(output_folder_path, dict1['name'] + '.zip')
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 保存CSV文件到zip
                csv_output = dict1['name'] + '.csv'
                result_data.to_csv(csv_output, index=False, header=True)
                zipf.write(csv_output, csv_output)
                os.remove(csv_output)  # 删除临时CSV文件

                # 拷贝和创建RawLogs目录到zip
                raw_log_zip_path = 'RawLogs'
                zip_copy_directory(debug_path, raw_log_zip_path, zipf, exclude_dir='Dump')

            total += 1

        print(total)
