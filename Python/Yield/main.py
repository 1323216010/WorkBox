import json
from compute import toDoTargetS
from utils import find_files
from utils import version
from utils import ensure_dir
from utils import generate_csv
from utils import generate_csv_final
from utils import save_list_as_json

def main():
    # 打开并读取JSON文件
    with open('config.json', 'r') as f:
        list = json.load(f)

    for obj in list:
        print("type", obj['type'], "--", obj['machine'])

    type = input('pls input type\n')
    data = [item for item in list if item["type"] == type][0]

    dir = input('pls input dir\n')
    paths = find_files(dir, data['stations'], ["LimitLog"], [".csv"])
    data['exception_files'] = []
    dfMerge, dfYield = toDoTargetS(paths, data)

    path = "results"
    ensure_dir(path)
    dfMerge.to_csv(path + "\\" + data['machine'] + '_PASS_FAIL_Result.csv', index=False)
    dfYield.to_csv(path + "\\" + data['machine'] + '_Yield_Result.csv', index=False)
    generate_csv(paths, data, path)

    if 'final' in data and data['final'] == False:
        pass
    else:
        generate_csv_final(dfMerge, paths, data, path)

    save_list_as_json(data['exception_files'], './results/exception_files.json')

if __name__ == '__main__':
    version()
    while(1):
        main()
        print("The task is complete, please click exit or continue")
        print("========================END=============================")
