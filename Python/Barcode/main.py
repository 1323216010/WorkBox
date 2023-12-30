import json
import os
import pandas as pd
from utils import get_dict, string_to_hex_list, actuator_barcode, find_files_with_list

def main():
    file_path = input("please enter the log path:")
    print("=======================START============================")

    with open('config.json', 'r', encoding='utf-8') as file:
        configs = json.load(file)
    vcmID = configs.get('vcmID', 'vcmID')
    bank11 = configs.get('#Bank11', '#Bank11')
    bank12 = configs.get('#Bank12', '#Bank12')
    bank11_number = -1*configs.get('#Bank11_number', 5)

    paths = find_files_with_list([file_path], [], ["LimitLog", "umath", "-testset-1", "-testset-2"], [".csv"])
    for file_path in paths:
        print(file_path)
        df = pd.read_csv(file_path, low_memory=False)

        if bank11 in df.columns and bank12 in df.columns:
            # 初始化vcmID列
            df[vcmID] = '-'

            # 遍历每一行
            for index, row in df.iterrows():
                try:
                    # 对每一行应用相应的处理
                    if row[bank11] != '-' and row[bank12] != '-':
                        vcm_id = actuator_barcode(get_dict(),
                                                  string_to_hex_list(row[bank11][2:])[bank11_number:] + string_to_hex_list(
                                                      row[bank12][2:]))
                        print(vcm_id)
                        df.at[index, vcmID] = vcm_id
                except Exception as e:
                    # 如果出现错误，打印错误信息（可选）并继续处理下一行
                    print(f"Error processing row {index}: {e}")

            # 保存修改后的DataFrame
            df.to_csv(file_path, index=False)
        else:
            raise ValueError("The required columns do not exist in the CSV file.")

        df.to_csv(file_path, index=False)

if __name__ == "__main__":
    while (1):
        # main()
        try:
            main()
            os.system("pause")
            print("The task is complete, please click exit or continue")
            print("========================END=============================")
        except Exception as e:
            print('The program has crashed unexpectedly, and the error message is:', e)
            os.system("pause")


