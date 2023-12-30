import os

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def find_substring_in_list(string, substr_list=['OQC-FTU', 'OQC-FTD', 'FTU', 'FTD', 'IGUANA', 'Gopher', 'Libra'], default='default'):
    for substr in substr_list:
        if substr in string:
            return substr
    return default

def replace_iguana(input_string):
    # 替换所有出现的IGUANA为Iguana
    return input_string.replace("Iguana", "IGUANA")


def replace_second_occurrence(A, B, C):
    # 查找B在A中第一次出现的位置
    first_occurrence = A.find(B)
    if first_occurrence == -1:
        # 如果B不在A中，直接返回A
        return A

    # 查找B在A中第二次出现的位置，从第一次出现的下一个位置开始查找
    second_occurrence = A.find(B, first_occurrence + len(B))
    if second_occurrence == -1:
        # 如果B在A中没有第二次出现，直接返回A
        return A

    # 替换第二次出现的B为C
    return A[:second_occurrence] + C + A[second_occurrence + len(B):]