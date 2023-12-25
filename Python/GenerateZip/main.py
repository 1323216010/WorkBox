import os
import pandas as pd
import zipfile
from utils import ensure_dir, find_files, extract_substring
from utils import insert
from utils import get_config
from utils import convert_datetime_format
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def zip_copy_directory(src, dst, ziph):
    for root, dirs, files in os.walk(src):
        for file in files:
            file_path = os.path.join(root, file)
            # 不创建子目录，所有文件直接放在dst目录下
            dst_path = os.path.join(dst, file)
            ziph.write(file_path, dst_path)

def main(path, output_folder_path, dict0):
    file_name = os.path.basename(path)
    data = pd.read_csv(path, header=None, dtype=str)
    data = data.dropna(axis=1, how='all')
    headers = data.iloc[0].tolist()
    upper_limit = data.iloc[1].tolist()
    lower_limit = data.iloc[2].tolist()

    total1 = 0
    dict1 = {}
    for index, row in data.iloc[3:].iterrows():
        try:
            result_data = pd.DataFrame([upper_limit, lower_limit, row.tolist()], columns=headers)

            insert(result_data, dict0)

            if 'build_num' in result_data.columns:
                result_data.at[2, 'build_num'] = dict0['build_num']

            if 'time' in result_data.columns:
                result_data.at[2, 'time'] = convert_datetime_format(result_data.at[2, 'time'])

            if 'ShieldCanSN_NVM' in result_data.columns:
                result_data.at[2, 'ShieldCanSN_NVM'] = result_data.at[2, 'HandlerBCD']

            global_time_stamp = result_data.loc[2, 'global_time_stamp']
            site = result_data.loc[2, 'Site'][-1]
            time = extract_substring(global_time_stamp)
            debug_path = os.path.join(os.path.dirname(path), 'Debug_' + site, time)

            barcode = result_data.loc[2, 'HandlerBCD']
            site_time = result_data.loc[2, 'SiteTime']
            dict1['name'] = 'VR_' + dict0['config'] + '_Gopher_' + site + '_' + barcode + '_' + site_time

            if 'DCKEY' in result_data.columns:
                result_data.at[2, 'DCKEY'] = site_time

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

                # 删除重复的列
                result_data = result_data.loc[:, ~result_data.columns.duplicated()]

                result_data.to_csv(csv_output, index=False, header=True)
                zipf.write(csv_output, csv_output)
                os.remove(csv_output)  # 删除临时CSV文件

                # 拷贝和创建RawLogs目录到zip
                raw_log_zip_path = 'RawLogs'
                zip_copy_directory(debug_path, raw_log_zip_path, zipf)
                total1 += 1
        except:
            dict0['path'] = dict0['path'] + 'fail row:' + row.tolist() + '\n'
            print(row.tolist())
    print(total1)
    return total1

if __name__ == '__main__':
    dict0 = get_config('config.json')

    if dict0['source_folder_path'].endswith('.json'):
        paths = get_config(dict0['source_folder_path'])
    else:
        source_folder_path = dict0['source_folder_path']
        paths = find_files(source_folder_path, ['Gopher_Tester'], ['LimitLog'], ['.csv'])

    output_folder_path = dict0['output_folder_path']
    ensure_dir(output_folder_path)

    dict0['path'] = ''
    total = 0
    for path in paths:
        try:
            total = total + main(path, output_folder_path, dict0)
            print()
        except:
            file_name = os.path.basename(path)

            dict0['path'] = dict0['path'] + 'fail path:' + path + '\n'

    print('total:', total)
    with open(dict0['listlog_path'], 'a') as file:
        file.write(dict0['path'])
    while(1):
        input('The task is complete, please click exit')
