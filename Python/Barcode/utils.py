import os

def get_dict():
    map_data = {
        0x0: ' ', 0x1: '0', 0x2: '1', 0x3: '2', 0x4: '3', 0x5: '4', 0x6: '5', 0x7: '6', 0x8: '7', 0x9: '8',
        0x0a: ' ', 0x0b: ' ', 0x0c: ' ', 0x0d: ' ', 0x0e: ' ', 0x0f: ' ',
        0x10: '9', 0x11: 'A', 0x12: 'B', 0x13: 'C', 0x14: 'D', 0x15: 'E', 0x16: 'F', 0x17: 'G', 0x18: 'H', 0x19: 'I',
        0x1a: ' ', 0x1b: ' ', 0x1c: ' ', 0x1d: ' ', 0x1e: ' ', 0x1f: ' ',
        0x20: 'J', 0x21: 'K', 0x22: 'L', 0x23: 'M', 0x24: 'N', 0x25: 'O', 0x26: 'P', 0x27: 'Q', 0x28: 'R', 0x29: 'S',
        0x2a: ' ', 0x2b: ' ', 0x2c: ' ', 0x2d: ' ', 0x2e: ' ', 0x2f: ' ',
        0x30: 'T', 0x31: 'U', 0x32: 'V', 0x33: 'W', 0x34: 'X', 0x35: 'Y', 0x36: 'Z',
        0x37: 'a', 0x38: 'b', 0x39: 'c',
        0x3a: ' ', 0x3b: ' ', 0x3c: ' ', 0x3d: ' ', 0x3e: ' ', 0x3f: ' ',
        0x40: 'd', 0x41: 'e', 0x42: 'f', 0x43: 'g', 0x44: 'h', 0x45: 'i', 0x46: 'j', 0x47: 'k', 0x48: 'l', 0x49: 'm',
        0x4a: ' ', 0x4b: ' ', 0x4c: ' ', 0x4d: ' ', 0x4e: ' ', 0x4f: ' ',
        0x50: 'n', 0x51: 'o', 0x52: 'p', 0x53: 'q', 0x54: 'r', 0x55: 's', 0x56: 't', 0x57: 'u', 0x58: 'v', 0x59: 'w',
        0x5a: ' ', 0x5b: ' ', 0x5c: ' ', 0x5d: ' ', 0x5e: ' ', 0x5f: ' ',
        0x60: 'x', 0x61: 'y', 0x62: 'z'
    }
    return map_data

def string_to_hex_list(input_string):
    hex_list = []
    # 每两个字符为一组进行遍历
    for i in range(0, len(input_string), 2):
        # 取出两个字符，并将其转换为16进制数
        hex_value = int(input_string[i:i+2], 16)
        # 将16进制数添加到列表中
        hex_list.append(hex_value)
    return hex_list

def actuator_barcode(map_data, buildInfo_ActuatorSN):
    strActuatorBarcode = [''] * 100

    strActuatorBarcode[0] = map_data[(buildInfo_ActuatorSN[0] >> 1) & 0x7F]
    strActuatorBarcode[1] = map_data[((buildInfo_ActuatorSN[0] << 6) & 0x40) + ((buildInfo_ActuatorSN[1] >> 2) & 0x3F)]
    strActuatorBarcode[2] = map_data[((buildInfo_ActuatorSN[1] << 5) & 0x60) + ((buildInfo_ActuatorSN[2] >> 3) & 0x1F)]
    strActuatorBarcode[3] = map_data[((buildInfo_ActuatorSN[2] << 4) & 0x70) + ((buildInfo_ActuatorSN[3] >> 4) & 0x0F)]
    strActuatorBarcode[4] = map_data[((buildInfo_ActuatorSN[3] << 3) & 0x78) + ((buildInfo_ActuatorSN[4] >> 5) & 0x07)]
    strActuatorBarcode[5] = map_data[((buildInfo_ActuatorSN[4] << 2) & 0x7C) + ((buildInfo_ActuatorSN[5] >> 6) & 0x03)]
    strActuatorBarcode[6] = map_data[((buildInfo_ActuatorSN[5] << 1) & 0x7E) + ((buildInfo_ActuatorSN[6] >> 7) & 0x01)]
    strActuatorBarcode[7] = map_data[buildInfo_ActuatorSN[6] & 0x7F]

    strActuatorBarcode[8] = map_data[(buildInfo_ActuatorSN[7] >> 1) & 0x7F]
    strActuatorBarcode[9] = map_data[((buildInfo_ActuatorSN[7] << 6) & 0x40) + ((buildInfo_ActuatorSN[8] >> 2) & 0x3F)]
    strActuatorBarcode[10] = map_data[((buildInfo_ActuatorSN[8] << 5) & 0x60) + ((buildInfo_ActuatorSN[9] >> 3) & 0x1F)]
    strActuatorBarcode[11] = map_data[
        ((buildInfo_ActuatorSN[9] << 4) & 0x70) + ((buildInfo_ActuatorSN[10] >> 4) & 0x0F)]
    strActuatorBarcode[12] = map_data[
        ((buildInfo_ActuatorSN[10] << 3) & 0x78) + ((buildInfo_ActuatorSN[11] >> 5) & 0x07)]
    strActuatorBarcode[13] = map_data[
        ((buildInfo_ActuatorSN[11] << 2) & 0x7C) + ((buildInfo_ActuatorSN[12] >> 6) & 0x03)]
    strActuatorBarcode[14] = map_data[
        ((buildInfo_ActuatorSN[12] << 1) & 0x7E) + ((buildInfo_ActuatorSN[13] >> 7) & 0x01)]
    strActuatorBarcode[15] = map_data[buildInfo_ActuatorSN[13] & 0x7F]

    return ''.join(strActuatorBarcode)


def find_files_with_list(paths, include_list, exclude_list, file_types, depth=None, match_all_includes=False):
    result = []

    for path in paths:
        path_depth = len(path.rstrip(os.sep).split(os.sep))

        for root, dirs, files in os.walk(path):
            current_depth = len(root.rstrip(os.sep).split(os.sep))
            if depth is not None and (current_depth - path_depth) >= depth:
                del dirs[:]
                continue

            for file in files:
                # 检查文件类型是否符合
                if not any(file.endswith(ft) for ft in file_types):
                    continue

                # 排除列表检查
                if any(substr in file for substr in exclude_list):
                    continue

                # 包含列表检查
                if include_list:
                    if match_all_includes:
                        if not all(substr in file for substr in include_list):
                            continue
                    else:
                        if not any(substr in file for substr in include_list):
                            continue

                # 添加符合条件的文件到结果列表
                result.append(os.path.join(root, file))

    return result

def print_version():
    print('DPCDeltaMap version is 20231229a')
    print("=========================================")
    print("Update Log")
    print("=========================================")
    print("[2023-12-29]")
    print("-----------------------------------------")
    print("Fixes:")
    print("    - Add crash prevention handling.")
    print("Features:")
    print("    - Add json configuration file.")
    print()
    print("For any questions or concerns, please contact:")
    print("Pengcheng.yan@cowellchina.com")
    print("=========================================")