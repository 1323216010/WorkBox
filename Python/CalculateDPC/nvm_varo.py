import numpy as np
import csv

def dp_correct_varo(idraw, nvm , dict1, file_name):
    """
    :param idraw: 原始图像数据
    :param varargs: 包含 NVM 数据的变量参数列表
    :return: 校正后的图像数据
    """

    # 创建 NVM 映射
    nvm_map = [[None for _ in range(256)] for _ in range(64)]
    for ind_page in range(256):
        for ind_byte in range(64):
            # 将十进制数字转换为十六进制字符串
            nvm_map[ind_byte][ind_page] = format(nvm[ind_byte][ind_page], 'x').upper()

    # 调用 NVM 解码函数
    fd_dp, spd_dp, dp101_dp, dp1001_dp, ZAF_DP, ZAFn_DP, pddc_dp, MPD_DP, Cluster_DP, CIT_DP = nvm_decode_dp_varo(nvm_map)

    # 将信息保存到CSV文件中
    with open(dict1['csv_path'] + '\\' + file_name + '_' + 'coordinates.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # 写入标题行
        writer.writerow(['Dictionary', 'Address_X', 'Address_Y'])

        # 为每个字典写入数据
        for name, d in [('fd_dp', fd_dp), ('spd_dp', spd_dp), ('dp101_dp', dp101_dp),
                        ('dp1001_dp', dp1001_dp), ('ZAF_DP', ZAF_DP), ('ZAFn_DP', ZAFn_DP), ('pddc_dp', pddc_dp), ('MPD_DP', MPD_DP),
                        ('Cluster_DP', Cluster_DP), ('CIT_DP', CIT_DP)]:
            if 'address_x' in d and 'address_y' in d:
                address_x = d['address_x']
                address_y = d['address_y']
                for x, y in zip(address_x, address_y):
                    writer.writerow([name, x, y])

    # 调用 DP 校正函数
    idraw_comp, rev = dp_comp_rev3p0(idraw, spd_dp, fd_dp, dp101_dp, dp1001_dp, ZAF_DP, ZAFn_DP, pddc_dp, MPD_DP, Cluster_DP, CIT_DP)

    return idraw_comp

def nvm_decode_dp_varo(nvm_map):
    """
    解码不同的数据点（DP）。

    :param nvm_map: NVM 映射数据
    :return: 包含各个 DP 信息的字典
    """
    rev = 2.5  # Brideville sensor 的版本

    # 调用 get_dp_number 函数来获取 DP 信息
    dp_info = get_dp_number(nvm_map)

    # 解包 dp_info 字典中的各个 DP 对象
    fd_dp = dp_info['FD_DP']
    spd_dp = dp_info['SPD_DP']
    dp101_dp = dp_info['DP101_DP']
    dp1001_dp = dp_info['DP1001_DP']
    ZAF_DP = dp_info['ZAF_DP']
    ZAFn_DP = dp_info['ZAFn_DP']
    pddc_dp = dp_info['PDDC_DP']
    MPD_DP = dp_info['MPD_DP']
    Cluster_DP = dp_info['Cluster_DP']
    CIT_DP = dp_info['CIT_DP']

    fd_dp = nvm_decode_fd(nvm_map, fd_dp)
    spd_dp = NVMDecodeSPD(nvm_map, spd_dp)
    dp101_dp = NVMDecodeDP101(nvm_map, dp101_dp)
    dp1001_dp = NVMDecodeDP1001(nvm_map, dp1001_dp)
    ZAF_DP = NVMDecodeZAF(nvm_map, ZAF_DP)
    ZAFn_DP = NVMDecodeZAFn(nvm_map, ZAFn_DP)
    pddc_dp = NVMDecodePDDC(nvm_map, pddc_dp)
    MPD_DP = NVMDecodeMPD(nvm_map, MPD_DP)

    Cluster_DP = NVMDecodeSpare1(nvm_map, Cluster_DP)
    CIT_DP = NVMDecodeZAF(nvm_map, CIT_DP)



    return fd_dp, spd_dp, dp101_dp, dp1001_dp, ZAF_DP, ZAFn_DP, pddc_dp, MPD_DP, Cluster_DP, CIT_DP

def get_dp_number(nvm_map):
    # 初始化 DP 对象
    dp_objects = {
        'FD_DP': {'addr_bit': 25, 'dp_per_tag': 8},
        'SPD_DP': {'addr_bit': 27, 'dp_bit_length_type': 2},
        'DP101_DP': {'addr_bit': 27, 'dp_bit_length_type': 2},
        'DP1001_DP': {'addr_bit': 26, 'dp_bit_length_type': 1},
        'ZAF_DP': {'addr_bit': 25},
        'ZAFn_DP': {'addr_bit': 25},
        'PDDC_DP': {'addr_bit': 25},
        'Cluster_DP': {'addr_bit': 25},
        'MPD_DP': {'addr_bit': 25},
        'CIT_DP': {'addr_bit': 25}
    }

    offset = 13
    nvm_address_num = 9344  # 初始 NVM 地址数字

    for dp_name, dp_info in dp_objects.items():
        if dp_name == 'ZAFn_DP' or dp_name == 'CIT_DP':
            # 对于 LongCIT_Cluster，需要处理两个 NVM 地址
            dp_number = 0
            for i in range(2):
                nvm_page = nvm_address_num[i] // 64
                nvm_byte = nvm_address_num[i] % 64
                # 确保高位字节优先
                dp_number = (dp_number << 8) + int(nvm_map[nvm_byte][nvm_page], 16)
            if dp_name == 'ZAFn_DP':
                nvm_address_num = nvm_address_num[1]  # 更新 nvm_address_num 为列表中的最后一个元素
            else:
                nvm_address_num = nvm_address_num[0]  # 更新 nvm_address_num 为列表中的第一个元素
        else:
            # 计算 NVM 页面和字节
            nvm_page = nvm_address_num // 64
            nvm_byte = nvm_address_num % 64
            dp_number = int(nvm_map[nvm_byte][nvm_page], 16)

        # 计算起始和结束地址
        if dp_name == 'FD_DP':
            dp_start_address = nvm_address_num + offset
        else:
            dp_start_address = dp_objects[prev_dp]['DP_endAddress'] + 1
        # dp_start_address = dp_objects[prev_dp]['DP_endAddress'] + 1

        dp_end_address = dp_start_address + np.ceil(dp_info['addr_bit'] * dp_number / 8) - 1

        # 更新 DP 对象信息
        dp_info.update({
            'number': dp_number,
            'DP_startAddress': int(dp_start_address),
            'DP_endAddress': int(dp_end_address)
        })

        prev_dp = dp_name  # 记录上一个处理的 DP 名称

        if dp_name == 'MPD_DP':
            nvm_address_num = [nvm_address_num + 2, nvm_address_num + 3]
        elif dp_name == 'ZAF_DP':
            nvm_address_num = [nvm_address_num + 1, nvm_address_num + 2]
        else:
            nvm_address_num = nvm_address_num + 1

    return dp_objects

def nvm_decode_fd(nvm_map, fd_dp):
    """
    解码 FD 数据点（DP）的地址。

    :param nvm_map: NVM 映射数据
    :param fd_dp: FD DP 的相关信息
    :return: 更新后的 FD DP 对象
    """
    dp_per_tag = 8
    dp_number = fd_dp['number']
    dp_start_address = fd_dp['DP_startAddress']
    dp_end_address = fd_dp['DP_endAddress']

    if dp_number > 0:
        dp_address_x_nvm, dp_address_y_nvm = NVMDecodeAddr(nvm_map, dp_number, dp_start_address, dp_end_address)

        dp_address_x = [0] * (dp_per_tag * dp_number)
        dp_address_y = [0] * (dp_per_tag * dp_number)

        for indx in range(dp_number):
            base_index = 8 * indx

            # 确保列表足够长
            while len(dp_address_x) < base_index + 3:
                dp_address_x.append(0)
                dp_address_y.append(0)

            # FD DP location
            dp_address_x[base_index] = dp_address_x_nvm[indx]
            dp_address_y[base_index] = dp_address_y_nvm[indx]
            # FD 2x4 - (0,1)
            dp_address_x[base_index + 1] = dp_address_x_nvm[indx] + 1
            dp_address_y[base_index + 1] = dp_address_y_nvm[indx] + 0
            # FD 2x4 - (0,2)
            dp_address_x[base_index + 2] = dp_address_x_nvm[indx] + 0
            dp_address_y[base_index + 2] = dp_address_y_nvm[indx] + 1
            # FD 2x4 - (0,3)
            dp_address_x[base_index + 3] = dp_address_x_nvm[indx] + 1
            dp_address_y[base_index + 3] = dp_address_y_nvm[indx] + 1

            dp_address_x[base_index + 4] = dp_address_x_nvm[indx] + 0
            dp_address_y[base_index + 4] = dp_address_y_nvm[indx] + 2

            dp_address_x[base_index + 5] = dp_address_x_nvm[indx] + 1
            dp_address_y[base_index + 5] = dp_address_y_nvm[indx] + 2

            dp_address_x[base_index + 6] = dp_address_x_nvm[indx] + 0
            dp_address_y[base_index + 6] = dp_address_y_nvm[indx] + 3

            dp_address_x[base_index + 7] = dp_address_x_nvm[indx] + 1
            dp_address_y[base_index + 7] = dp_address_y_nvm[indx] + 3


        indx_dp = [i for i, (x, y) in enumerate(zip(dp_address_x, dp_address_y)) if x > 0 and y > 0]
        dp_number = len(indx_dp) // dp_per_tag
        dp_address_x = [dp_address_x[i] for i in indx_dp]
        dp_address_y = [dp_address_y[i] for i in indx_dp]

        fd_dp['number'] = dp_number * 8
        fd_dp['address_x'] = dp_address_x
        fd_dp['address_y'] = dp_address_y

    elif dp_number == 0:  # 无标记的 DP
        fd_dp['number'] = 0
        fd_dp['address_x'] = []
        fd_dp['address_y'] = []

    else:  # DP 数量标记错误
        raise ValueError('NVM 解码错误，错误的 DP 数量')

    return fd_dp

def NVMDecodeAddr(nvm_map, dp_number, dp_start_address, dp_end_address):
    """
    解析 NVM 地图，提取 FD 数据点的 X 和 Y 坐标。

    :param nvm_map: NVM 映射数据
    :param dp_number: 数据点的数量
    :param dp_start_address: 数据点起始地址
    :param dp_end_address: 数据点结束地址
    :return: X 坐标列表和 Y 坐标列表
    """
    dp_addr_offset_x = 0  # 仅用于 PIT
    dp_addr_offset_y = 0  # 仅用于 PIT
    dp_addr_bit_length_x = 13
    dp_addr_bit_length_y = 12

    nvm_page = dp_start_address // 64
    nvm_byte = dp_start_address % 64
    nvm_dp_byte_num = dp_end_address - dp_start_address + 1
    nvm_binary = ""

    if nvm_dp_byte_num > 0:
        for indx in range(nvm_dp_byte_num):
            nvm_binary_tmp = format(int(nvm_map[nvm_byte][nvm_page], 16), '08b')
            nvm_binary += nvm_binary_tmp
            nvm_byte += 1
            if nvm_byte > 63:
                nvm_page += 1
                nvm_byte = 0

        dp_address_x_nvm = []
        dp_address_y_nvm = []

        binary_count = 0
        for indx in range(dp_number):
            # X 地址
            dp_address_x_tmp = int(nvm_binary[binary_count:binary_count + dp_addr_bit_length_x], 2)
            dp_address_x_tmp -= dp_addr_offset_x  # 偏移修正
            dp_address_x_tmp += 1  # Python 从 0 开始，MATLAB 从 1 开始
            dp_address_x_nvm.append(dp_address_x_tmp)
            binary_count += dp_addr_bit_length_x

            # Y 地址
            dp_address_y_tmp = int(nvm_binary[binary_count:binary_count + dp_addr_bit_length_y], 2)
            dp_address_y_tmp -= dp_addr_offset_y  # 偏移修正
            dp_address_y_tmp += 1  # Python 从 0 开始，MATLAB 从 1 开始
            dp_address_y_nvm.append(dp_address_y_tmp)
            binary_count += dp_addr_bit_length_y
    else:
        dp_address_x_nvm = []
        dp_address_y_nvm = []

    return dp_address_x_nvm, dp_address_y_nvm

def NVMDecodeSPD(NVM_MAP, SPD_DP):
    DP_perTag = 2
    DP_number = SPD_DP['number']
    DP_startAddress = SPD_DP['DP_startAddress']
    DP_endAddress = SPD_DP['DP_endAddress']
    DP_addr_bitLength_type = SPD_DP['dp_bit_length_type']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM, DP_address_type = NVMDecodeAddrType(NVM_MAP, DP_number, DP_startAddress,
                                                                                DP_endAddress, DP_addr_bitLength_type)

        DP_address_x = [0] * (DP_perTag * DP_number)
        DP_address_y = [0] * (DP_perTag * DP_number)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

            if DP_address_type[indx] == 0:
                DP_address_x[2 * indx + 1] = DP_address_x[2 * indx] + 2
                DP_address_y[2 * indx + 1] = DP_address_y[2 * indx] + 0
            elif DP_address_type[indx] == 1:
                DP_address_x[2 * indx + 1] = DP_address_x[2 * indx] + 2
                DP_address_y[2 * indx + 1] = DP_address_y[2 * indx] + 2
            elif DP_address_type[indx] == 2:
                DP_address_x[2 * indx + 1] = DP_address_x[2 * indx] + 0
                DP_address_y[2 * indx + 1] = DP_address_y[2 * indx] + 2
            elif DP_address_type[indx] == 3:
                DP_address_x[2 * indx + 1] = DP_address_x[2 * indx] - 2
                DP_address_y[2 * indx + 1] = DP_address_y[2 * indx] + 2

        indx_DP = [i for i in range(len(DP_address_x)) if DP_address_x[i] > 0 and DP_address_y[i] > 0]
        DP_number = len(indx_DP) // 2
        DP_address_x = [DP_address_x[i] for i in indx_DP]
        DP_address_y = [DP_address_y[i] for i in indx_DP]
        DP_address_type = DP_address_type[:DP_number]

        SPD_DP['number'] = DP_number * DP_perTag
        SPD_DP['address_x'] = DP_address_x
        SPD_DP['address_y'] = DP_address_y
        SPD_DP['type'] = DP_address_type

    elif DP_number == 0:  # no DP tagged
        SPD_DP['number'] = 0
        SPD_DP['address_x'] = []
        SPD_DP['address_y'] = []
        SPD_DP['type'] = []

    else:  # no DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return SPD_DP

def NVMDecodeAddrType(NVM_MAP, DP_number, DP_startAddress, DP_endAddress, DP_addr_bitLength_type):
    DP_addr_offset_x = 0  # X轴偏移量
    DP_addr_offset_y = 0  # Y轴偏移量
    DP_addr_bitLength_x = 13  # X轴地址的位长度
    DP_addr_bitLength_y = 12  # Y轴地址的位长度

    NVM_Page = DP_startAddress // 64
    NVM_Byte = DP_startAddress % 64
    NVM_DP_Byte_num = DP_endAddress - DP_startAddress + 1
    NVM_binary = ""

    if NVM_DP_Byte_num > 0:
        for indx in range(NVM_DP_Byte_num):
            NVM_binary_tmp = format(int(NVM_MAP[NVM_Byte][NVM_Page], 16), '08b')
            NVM_binary += NVM_binary_tmp
            NVM_Byte += 1
            if NVM_Byte > 63:
                NVM_Page += 1
                NVM_Byte = 0

        DP_Address_X_NVM = np.zeros(DP_number, dtype=int)
        DP_Address_Y_NVM = np.zeros(DP_number, dtype=int)
        DP_Address_type = np.zeros(DP_number, dtype=int)

        binary_count = 0
        for indx in range(DP_number):
            # 解析X轴地址
            DP_address_x_tmp = int(NVM_binary[binary_count:binary_count + DP_addr_bitLength_x], 2)
            DP_address_x_tmp = DP_address_x_tmp - DP_addr_offset_x  # 应用偏移量
            DP_address_x_tmp += 1  # Python是从0开始计数
            DP_Address_X_NVM[indx] = DP_address_x_tmp
            binary_count += DP_addr_bitLength_x

            # 解析Y轴地址
            DP_address_y_tmp = int(NVM_binary[binary_count:binary_count + DP_addr_bitLength_y], 2)
            DP_address_y_tmp = DP_address_y_tmp - DP_addr_offset_y  # 应用偏移量
            DP_address_y_tmp += 1  # Python是从0开始计数
            DP_Address_Y_NVM[indx] = DP_address_y_tmp
            binary_count += DP_addr_bitLength_y

            # 解析类型
            DP_Address_type[indx] = int(NVM_binary[binary_count:binary_count + DP_addr_bitLength_type], 2)
            binary_count += DP_addr_bitLength_type
    else:
        DP_Address_X_NVM = np.array([])
        DP_Address_Y_NVM = np.array([])

    return DP_Address_X_NVM, DP_Address_Y_NVM, DP_Address_type

def NVMDecodeDP101(NVM_MAP, DP101_DP):
    DP_perTag = 2
    DP_number = DP101_DP['number']
    DP_startAddress = DP101_DP['DP_startAddress']
    DP_endAddress = DP101_DP['DP_endAddress']
    DP_addr_bitLength_type = DP101_DP['dp_bit_length_type']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM, DP_address_type = NVMDecodeAddrType(NVM_MAP, DP_number, DP_startAddress, DP_endAddress, DP_addr_bitLength_type)

        DP_address_x = np.zeros(DP_perTag * DP_number, dtype=int)
        DP_address_y = np.zeros(DP_perTag * DP_number, dtype=int)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

            # 根据类型确定101 DP的位置
            if DP_address_type[indx] == 0:
                DP_address_x[DP_perTag * indx + 1] = DP_address_x[DP_perTag * indx] + 4
                DP_address_y[DP_perTag * indx + 1] = DP_address_y[DP_perTag * indx]
            elif DP_address_type[indx] == 1:
                DP_address_x[DP_perTag * indx + 1] = DP_address_x[DP_perTag * indx] + 4
                DP_address_y[DP_perTag * indx + 1] = DP_address_y[DP_perTag * indx] + 4
            elif DP_address_type[indx] == 2:
                DP_address_x[DP_perTag * indx + 1] = DP_address_x[DP_perTag * indx]
                DP_address_y[DP_perTag * indx + 1] = DP_address_y[DP_perTag * indx] + 4
            elif DP_address_type[indx] == 3:
                DP_address_x[DP_perTag * indx + 1] = DP_address_x[DP_perTag * indx] - 4
                DP_address_y[DP_perTag * indx + 1] = DP_address_y[DP_perTag * indx] + 4

        # 过滤无效的DP地址
        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP) // DP_perTag
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]
        DP_address_type = DP_address_type[:DP_number]

        DP101_DP['number'] = DP_perTag * DP_number
        DP101_DP['address_x'] = DP_address_x
        DP101_DP['address_y'] = DP_address_y
        DP101_DP['type'] = DP_address_type

    elif DP_number == 0:  # 没有标记的DP
        DP101_DP['number'] = 0
        DP101_DP['address_x'] = []
        DP101_DP['address_y'] = []
        DP101_DP['type'] = []
    else:  # DP数量标记错误
        raise ValueError('NVM解码错误，DP数量错误')

    return DP101_DP

def NVMDecodeDP1001(NVM_MAP, DP1001_DP):
    DP_perTag = 1
    DP_number = DP1001_DP['number']
    DP_startAddress = DP1001_DP['DP_startAddress']
    DP_endAddress = DP1001_DP['DP_endAddress']
    DP_addr_bitLength_type = DP1001_DP['dp_bit_length_type']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM, DP_address_type = NVMDecodeAddrType(NVM_MAP, DP_number, DP_startAddress,
                                                                                DP_endAddress, DP_addr_bitLength_type)

        DP_address_x = np.zeros(DP_perTag * DP_number)
        DP_address_y = np.zeros(DP_perTag * DP_number)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

            # Couplet DP location based on type
            # skip type for 1-0-0-1 for now
            if DP_address_type[indx] == 0:
                pass
            elif DP_address_type[indx] == 1:
                pass

        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP) // DP_perTag
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]
        DP_address_type = DP_address_type[:DP_number]

        DP1001_DP['number'] = DP_number
        DP1001_DP['address_x'] = DP_address_x
        DP1001_DP['address_y'] = DP_address_y
        DP1001_DP['type'] = DP_address_type
    elif DP_number == 0:  # no DP tagged
        DP1001_DP['number'] = 0
        DP1001_DP['address_x'] = []
        DP1001_DP['address_y'] = []
        DP1001_DP['type'] = []
    else:  # no DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return DP1001_DP

def NVMDecodeZAF(NVM_MAP, ZAF_DP):
    DP_perTag = 1
    DP_number = ZAF_DP['number']
    DP_startAddress = ZAF_DP['DP_startAddress']
    DP_endAddress = ZAF_DP['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress)

        DP_address_x = np.zeros(DP_perTag * DP_number)
        DP_address_y = np.zeros(DP_perTag * DP_number)
        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP)
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]

        ZAF_DP['number'] = DP_number
        ZAF_DP['address_x'] = DP_address_x
        ZAF_DP['address_y'] = DP_address_y

    elif DP_number == 0:  # no DP tagged
        ZAF_DP['number'] = 0
        ZAF_DP['address_x'] = np.array([])
        ZAF_DP['address_y'] = np.array([])

    else:  # DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return ZAF_DP

def NVMDecodeZAFn(NVM_MAP, ZAFn_DP):
    # This function is identical to NVMDecodeZAF, so you can just call
    return NVMDecodeZAF(NVM_MAP, ZAFn_DP)

def NVMDecodeMPD(NVM_MAP, MPD_DP):
    # This function is also identical to NVMDecodeZAF, so you can just call
    return NVMDecodeZAF(NVM_MAP, MPD_DP)

def NVMDecodePDDC(NVM_MAP, PDDC_DP):
    DP_perTag = 1
    DP_number = PDDC_DP['number']
    DP_startAddress = PDDC_DP['DP_startAddress']
    DP_endAddress = PDDC_DP['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress)

        DP_address_x = np.zeros(DP_perTag * DP_number)
        DP_address_y = np.zeros(DP_perTag * DP_number)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP)
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]

        PDDC_DP['number'] = DP_number
        PDDC_DP['address_x'] = DP_address_x
        PDDC_DP['address_y'] = DP_address_y
    elif DP_number == 0: # no DP tagged
        PDDC_DP['number'] = 0
        PDDC_DP['address_x'] = []
        PDDC_DP['address_y'] = []
    else: # no DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return PDDC_DP

def NVMDecodepix3_cluster(NVM_MAP, pix3_cluster):
    DP_perTag = 1
    DP_number = pix3_cluster['number']
    DP_startAddress = pix3_cluster['DP_startAddress']
    DP_endAddress = pix3_cluster['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress)

        DP_address_x = np.zeros(DP_perTag * DP_number, dtype=int)
        DP_address_y = np.zeros(DP_perTag * DP_number, dtype=int)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP)
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]

        pix3_cluster['number'] = DP_number
        pix3_cluster['address_x'] = DP_address_x
        pix3_cluster['address_y'] = DP_address_y

    elif DP_number == 0:  # no DP tagged
        pix3_cluster['number'] = 0
        pix3_cluster['address_x'] = np.array([])
        pix3_cluster['address_y'] = np.array([])

    else:  # DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return pix3_cluster

def NVMDecodeHL(NVM_MAP, HL_DP):
    DP_perTag = 1
    DP_number = HL_DP['number']
    DP_startAddress = HL_DP['DP_startAddress']
    DP_endAddress = HL_DP['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress)

        DP_address_x = np.zeros(DP_perTag * DP_number, dtype=int)
        DP_address_y = np.zeros(DP_perTag * DP_number, dtype=int)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP)
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]

        HL_DP['number'] = DP_number
        HL_DP['address_x'] = DP_address_x
        HL_DP['address_y'] = DP_address_y

    elif DP_number == 0:  # no DP tagged
        HL_DP['number'] = 0
        HL_DP['address_x'] = np.array([])
        HL_DP['address_y'] = np.array([])

    else:  # DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return HL_DP

def NVMDecodeSpare1(NVM_MAP, SPARE1):
    DP_perTag = 1
    DP_number = SPARE1['number']
    DP_startAddress = SPARE1['DP_startAddress']
    DP_endAddress = SPARE1['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress)

        DP_address_x = np.zeros(DP_perTag * DP_number, dtype=int)
        DP_address_y = np.zeros(DP_perTag * DP_number, dtype=int)

        for indx in range(1, DP_number + 1):
            DP_address_x[DP_perTag * (indx - 1)] = DP_Address_X_NVM[indx - 1]
            DP_address_y[DP_perTag * (indx - 1)] = DP_Address_Y_NVM[indx - 1]

        indx_DP = np.where((DP_address_x > 0) & (DP_address_y > 0))[0]
        DP_number = len(indx_DP)
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]

        SPARE1['number'] = DP_number
        SPARE1['address_x'] = DP_address_x
        SPARE1['address_y'] = DP_address_y

    elif DP_number == 0:  # no DP tagged
        SPARE1['number'] = 0
        SPARE1['address_x'] = np.array([])
        SPARE1['address_y'] = np.array([])

    else:  # DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return SPARE1

def NVMDecodeLongCIT_Cluster(NVM_MAP, LongCIT_Cluster):
    DP_perTag = 1
    DP_number = LongCIT_Cluster['number']
    DP_startAddress = LongCIT_Cluster['DP_startAddress']
    DP_endAddress = LongCIT_Cluster['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress)

        DP_address_x = np.zeros(DP_perTag * DP_number, dtype=int)
        DP_address_y = np.zeros(DP_perTag * DP_number, dtype=int)

        for indx in range(DP_number):
            DP_address_x[DP_perTag * indx] = DP_Address_X_NVM[indx]
            DP_address_y[DP_perTag * indx] = DP_Address_Y_NVM[indx]

        indx_DP = np.where(DP_address_x > 0)[0]
        DP_number = len(indx_DP)
        DP_address_x = DP_address_x[indx_DP]
        DP_address_y = DP_address_y[indx_DP]

        LongCIT_Cluster['number'] = DP_number
        LongCIT_Cluster['address_x'] = DP_address_x
        LongCIT_Cluster['address_y'] = DP_address_y

    elif DP_number == 0:  # no DP tagged
        LongCIT_Cluster['number'] = 0
        LongCIT_Cluster['address_x'] = np.array([])
        LongCIT_Cluster['address_y'] = np.array([])

    else:  # DP number is tagged wrong
        raise ValueError('NVM decode wrong, wrong DP number')

    return LongCIT_Cluster

def coordinate_rotated_180(dp):
    # 旋转列表中的每个坐标
    dp['address_x'] = [4224 - x + 1 for x in dp['address_x']]
    dp['address_y'] = [3024 - y + 1 for y in dp['address_y']]
    return dp

def dp_comp_rev3p0(IDraw,SPD_DP,FD_DP,DP101_DP,DP1001_DP,ZAF_DP,ZAFn_DP,PDDC_DP,MPD_DP,Cluster3_DP,CIT_DP):
    rev = '2.032'  # 版本号

    h, w = IDraw.shape
    IDrawComp = np.copy(IDraw)

    Couplet_DP_number = SPD_DP['number']
    Couplet_DP_number = Couplet_DP_number // 2  # 成对的数量
    DP_address_x_Couplet = SPD_DP['address_x']
    DP_address_y_Couplet = SPD_DP['address_y']
    DP_type_Couplet = SPD_DP['type']

    for indx in range(Couplet_DP_number):
        type_tmp = DP_type_Couplet[indx]

        x_tmp_1 = DP_address_x_Couplet[(indx) * 2] - 1
        x_tmp_2 = DP_address_x_Couplet[(indx + 1) * 2 - 1] - 1
        y_tmp_1 = DP_address_y_Couplet[(indx) * 2] - 1
        y_tmp_2 = DP_address_y_Couplet[(indx + 1) * 2 - 1] - 1 # 仅适用于EW传感器设置v3翻转
        if type_tmp == 0:
            if 3 <= x_tmp_1 <= w - 4:
                IDrawComp[y_tmp_1, x_tmp_1] = (2 * IDraw[y_tmp_1, x_tmp_1 - 2] + IDraw[y_tmp_1, x_tmp_1 + 4]) // 3
                IDrawComp[y_tmp_2, x_tmp_2] = (IDraw[y_tmp_1, x_tmp_1 - 2] + 2 * IDraw[y_tmp_1, x_tmp_1 + 4]) // 3
            elif x_tmp_1 < 3:
                IDrawComp[y_tmp_1, x_tmp_1] = IDraw[y_tmp_1, x_tmp_1 + 4]
                IDrawComp[y_tmp_2, x_tmp_2] = IDraw[y_tmp_1, x_tmp_1 + 4]
            elif x_tmp_1 > w - 4:
                if x_tmp_1 <= w:
                    IDrawComp[y_tmp_1, x_tmp_1] = IDraw[y_tmp_1, x_tmp_1 - 2]
                if x_tmp_2 <= w:
                    IDrawComp[y_tmp_2, x_tmp_2] = IDraw[y_tmp_1, x_tmp_1 - 2]
        else:
            if 3 <= x_tmp_1 <= w - 2:
                IDrawComp[y_tmp_1, x_tmp_1] = (IDraw[y_tmp_1, x_tmp_1 - 2] + IDraw[y_tmp_1, x_tmp_1 + 2]) // 2
            elif x_tmp_1 < 3:
                IDrawComp[y_tmp_1, x_tmp_1] = IDraw[y_tmp_1, x_tmp_1 + 2]
            elif w - 2 < x_tmp_1 <= w:
                IDrawComp[y_tmp_1, x_tmp_1] = IDraw[y_tmp_1, x_tmp_1 - 2]

            if 3 <= x_tmp_2 <= w - 2:
                IDrawComp[y_tmp_2, x_tmp_2] = (IDraw[y_tmp_2, x_tmp_2 - 2] + IDraw[y_tmp_2, x_tmp_2 + 2]) // 2
            elif x_tmp_2 < 3:
                IDrawComp[y_tmp_2, x_tmp_2] = IDraw[y_tmp_2, x_tmp_2 + 2]
            elif w - 2 < x_tmp_2 <= w:
                IDrawComp[y_tmp_2, x_tmp_2] = IDraw[y_tmp_2, x_tmp_2 - 2]

    DP_number_total = sum([d['number'] for d in [FD_DP, DP101_DP, DP1001_DP, ZAF_DP, ZAFn_DP, PDDC_DP, MPD_DP, CIT_DP]])
    DP_address_x_total = np.concatenate([d['address_x'] for d in [FD_DP, DP101_DP, DP1001_DP, ZAF_DP, ZAFn_DP, PDDC_DP, MPD_DP, CIT_DP]])
    DP_address_y_total = np.concatenate([d['address_y'] for d in [FD_DP, DP101_DP, DP1001_DP, ZAF_DP, ZAFn_DP, PDDC_DP, MPD_DP, CIT_DP]])

    for indx in range(DP_number_total):
        x_tmp = int(DP_address_x_total[indx]) - 1
        y_tmp = int(DP_address_y_total[indx]) - 1
        if 3 <= x_tmp <= w - 2:
            IDrawComp[y_tmp, x_tmp] = (IDraw[y_tmp, x_tmp - 2] + IDraw[y_tmp, x_tmp + 2]) // 2
        elif x_tmp < 3:
            IDrawComp[y_tmp, x_tmp] = IDraw[y_tmp, x_tmp + 2]
        elif w - 2 < x_tmp <= w:
            IDrawComp[y_tmp, x_tmp] = IDraw[y_tmp, x_tmp - 2]

    # 3px簇补偿
    clusterDP_number_total = Cluster3_DP['number']
    clusterDP_address_x_total = Cluster3_DP['address_x']
    clusterDP_address_y_total = Cluster3_DP['address_y']

    # 通过颜色填充补偿图像的两行两列
    ID_pad = np.zeros((h + 4, w + 4), dtype=IDrawComp.dtype)
    ID_pad[2:-2, 2:-2] = IDrawComp

    # 水平填充
    ID_pad[2:-2, 1] = IDrawComp[:, 1]
    ID_pad[2:-2, 0] = IDrawComp[:, 2]
    ID_pad[2:-2, -3] = IDrawComp[:, -2]
    ID_pad[2:-2, -4] = IDrawComp[:, -3]

    # 垂直填充
    ID_pad[1, :] = ID_pad[3, :]
    ID_pad[0, :] = ID_pad[4, :]
    ID_pad[-3, :] = ID_pad[-2, :]
    ID_pad[-4, :] = ID_pad[-1, :]

    for indx in range(clusterDP_number_total):
        x_tmp = clusterDP_address_x_total[indx] + 2
        y_tmp = clusterDP_address_y_total[indx] + 2

        # 用邻居的中值替换
        neighbors = [ID_pad[y_tmp - 2, x_tmp - 2], ID_pad[y_tmp, x_tmp - 2], ID_pad[y_tmp + 2, x_tmp - 2],
                     ID_pad[y_tmp - 2, x_tmp], ID_pad[y_tmp + 2, x_tmp],
                     ID_pad[y_tmp - 2, x_tmp + 2], ID_pad[y_tmp, x_tmp + 2], ID_pad[y_tmp + 2, x_tmp + 2]]

        IDrawComp[y_tmp - 2, x_tmp - 2] = np.median(neighbors).astype(IDrawComp.dtype)

    return IDrawComp, rev