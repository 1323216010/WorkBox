import os
import time
from dpc1 import get_map
from utils import get_config
from utils import find_files
from utils import ensure_dir
from utils import find_bounding_box
from utils import print_version

dict1 = {}
def main():
    dict1 = get_config('config.json')

    ensure_dir(dict1['csv_path'])
    ensure_dir(dict1['log_path'])

    dict1['points'] = find_bounding_box(dict1['locations'], dict1['range'])

    if 'path' in dict1:
        path = dict1['path']
    else:
        path = input("Please enter the images path: ")

    print("=======================START============================")
    # 记录开始时间点
    start_time = time.time()

    files = find_files(path, [], [], ['.raw'])

    for file in files:
        get_map(file, dict1)

    # 记录结束时间点
    end_time = time.time()
    print("cost time：", round(end_time - start_time, 1), "s")
    print("The task is complete, please click exit or continue")
    print("========================END=============================")

if __name__ == "__main__":
    print_version()
    while (1):
        main()
        os.system("pause")
        # try:
        #     main()
        #     os.system("pause")
        # except Exception as e:
        #     print('The program has crashed unexpectedly, and the error message is:', e)
        #     os.system("pause")

