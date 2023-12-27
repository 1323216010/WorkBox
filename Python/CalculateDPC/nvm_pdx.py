import numpy as np
import csv
from scipy.ndimage import median_filter

def dp_correct_pdx(idraw, nvm , dict1, file_name):
    """
    :param idraw: 原始图像数据
    :param varargs: 包含 NVM 数据的变量参数列表
    :return: 校正后的图像数据
    """

    # 创建 NVM 映射
    nvm_map = [[None for _ in range(512)] for _ in range(64)]
    for ind_page in range(512):
        for ind_byte in range(64):
            # 将十进制数字转换为十六进制字符串
            nvm_map[ind_byte][ind_page] = format(nvm[ind_byte][ind_page], 'x').upper()

    # 调用 NVM 解码函数
    fd_dp, HL_Single_DP, ZAF_DP, Neighbor_DP, dp101_dp, dp1001_dp, Cluster_DP, LCCD_DP = nvm_decode_dp_pdx(nvm_map)

    # 将信息保存到CSV文件中
    with open(dict1['csv_path'] + '\\' + file_name + '_' + 'coordinates.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # 写入标题行
        writer.writerow(['Dictionary', 'Address_X', 'Address_Y'])

        # 为每个字典写入数据
        for name, d in [('fd_dp', fd_dp), ('HL_Single_DP', HL_Single_DP), ('ZAF_DP', ZAF_DP), ('Neighbor_DP', Neighbor_DP), ('dp101_dp', dp101_dp),
                        ('dp1001_dp', dp1001_dp), ('Cluster_DP', Cluster_DP), ('LCCD_DP', LCCD_DP)]:
            if 'address_x' in d and 'address_y' in d:
                address_x = d['address_x']
                address_y = d['address_y']
                for x, y in zip(address_x, address_y):
                    writer.writerow([name, x, y])

    Decoded_DP = {}
    Decoded_DP['FD_DP'] = fd_dp
    Decoded_DP['HL_Single_DP'] = HL_Single_DP
    Decoded_DP['ZAF_DP'] = ZAF_DP
    Decoded_DP['Neighbor_DP'] = Neighbor_DP
    Decoded_DP['DP101_DP'] = dp101_dp
    Decoded_DP['DP1001_DP'] = dp1001_dp
    Decoded_DP['Cluster_DP'] = Cluster_DP
    Decoded_DP['LCCD_DP'] = LCCD_DP
    # 调用 DP 校正函数
    idraw_comp = DP_Comp_PDX(idraw, Decoded_DP)

    return idraw_comp

def nvm_decode_dp_pdx(nvm_map):
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
    HL_Single_DP = dp_info['HL_Single_DP']
    ZAF_DP = dp_info['ZAF_DP']
    Neighbor_DP = dp_info['Neighbor_DP']
    dp101_dp = dp_info['DP101_DP']
    dp1001_dp = dp_info['DP1001_DP']
    Cluster_DP = dp_info['Cluster_DP']
    LCCD_DP = dp_info['LCCD_DP']

    fd_dp = nvm_decode_fd(nvm_map, fd_dp)
    HL_Single_DP = NVMDecodeZAF(nvm_map, HL_Single_DP)
    ZAF_DP = NVMDecodeZAF(nvm_map, ZAF_DP)
    Neighbor_DP = NVMDecodeZAF(nvm_map, Neighbor_DP)
    dp101_dp = NVMDecodeDP101(nvm_map, dp101_dp)
    dp1001_dp = NVMDecodeDP1001(nvm_map, dp1001_dp)
    Cluster_DP = NVMDecodeSpare1(nvm_map, Cluster_DP)
    LCCD_DP = NVMDecodeLCCD_DP(nvm_map, LCCD_DP)


    return fd_dp, HL_Single_DP, ZAF_DP, Neighbor_DP, dp101_dp, dp1001_dp, Cluster_DP, LCCD_DP

def get_dp_number(nvm_map):
    # 初始化 DP 对象
    dp_objects = {
        'FD_DP': {'addr_bit': 27, 'dp_per_tag': 8},
        'HL_Single_DP': {'addr_bit': 27},
        'ZAF_DP': {'addr_bit': 27},
        'Neighbor_DP': {'addr_bit': 27},
        'DP101_DP': {'addr_bit': 27, 'dp_bit_length_type': 2},
        'DP1001_DP': {'addr_bit': 26, 'dp_bit_length_type': 1},
        'Cluster_DP': {'addr_bit': 25},
        'LCCD_DP': {'addr_bit': 25}
    }

    NVM_Address_Base = 12544
    nvm_address_num = [12544, 12545]  # 初始 NVM 地址数字

    for dp_name, dp_info in dp_objects.items():
        if dp_name == 'FD_DP' or dp_name == 'HL_Single_DP' or dp_name == 'ZAF_DP' or dp_name == 'Neighbor_DP' or dp_name == 'LCCD_DP':
            # 对于 LongCIT_Cluster，需要处理两个 NVM 地址
            dp_number = 0
            for i in range(2):
                nvm_page = nvm_address_num[i] // 64
                nvm_byte = nvm_address_num[i] % 64
                # 确保高位字节优先
                dp_number = (dp_number << 8) + int(nvm_map[nvm_byte][nvm_page], 16)

            nvm_address_num = [nvm_address_num[0] + 2, nvm_address_num[1] + 2]
        else:
            # 计算 NVM 页面和字节
            nvm_page = nvm_address_num // 64
            nvm_byte = nvm_address_num % 64
            dp_number = int(nvm_map[nvm_byte][nvm_page], 16)

        # 计算起始和结束地址
        if dp_name == 'FD_DP':
            dp_start_address = 12563
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

        if dp_name == 'Neighbor_DP':
            nvm_address_num = 12544 + 8
        elif dp_name == 'DP101_DP' or dp_name == 'DP1001_DP':
            nvm_address_num += 1
        elif dp_name == 'Cluster_DP':
            nvm_address_num = [NVM_Address_Base + 11, NVM_Address_Base + 12]

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

def NVMDecodeAddr(nvm_map, dp_number, dp_start_address, dp_end_address, Qmode=False):
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
    if Qmode:
        dp_addr_bit_length_x = 13
        dp_addr_bit_length_y = 12
    else:
        dp_addr_bit_length_x = 14
        dp_addr_bit_length_y = 13


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

def NVMDecodeLCCD_DP(NVM_MAP, ZAF_DP):
    DP_perTag = 1
    DP_number = ZAF_DP['number']
    DP_startAddress = ZAF_DP['DP_startAddress']
    DP_endAddress = ZAF_DP['DP_endAddress']

    if DP_number > 0:
        DP_Address_X_NVM, DP_Address_Y_NVM = NVMDecodeAddr(NVM_MAP, DP_number, DP_startAddress, DP_endAddress, True)

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


def DP_Comp_PDX(idraw, decoded_dp, debug_flag=True):
    # 解码DP信息
    FD_DP = decoded_dp['FD_DP']
    HL_Single_DP = decoded_dp['HL_Single_DP']
    ZAF_DP = decoded_dp['ZAF_DP']
    Neighbor_DP = decoded_dp['Neighbor_DP']
    DP101_DP = decoded_dp['DP101_DP']
    DP1001_DP = decoded_dp['DP1001_DP']
    Cluster_DP = decoded_dp['Cluster_DP']

    h, w = idraw.shape

    idraw_comp = idraw.copy()

    dp_address_xy_total_all = []

    # 补偿48M (Qsub) FD_DP 在12M图像中
    dp_number = FD_DP['number']
    dp_address_x = FD_DP['address_x']
    dp_address_y = FD_DP['address_y']

    dp_address_xy_total = np.unique(np.ceil(np.array([dp_address_x, dp_address_y]).T / 2), axis=0)
    dp_number_total = dp_address_xy_total.shape[0]
    dp_address_x_total = dp_address_xy_total[:, 0]
    dp_address_y_total = dp_address_xy_total[:, 1]

    if dp_number_total:
        if debug_flag:
            dp_type_total = ['FD_DP'] * (FD_DP['number'] // FD_DP['dp_per_tag'])
            dp_address_xy_total_all.append({
                'dp_address_x_total': dp_address_x_total,
                'dp_address_y_total': dp_address_y_total,
                'dp_type_total': dp_type_total
            })

        if dp_number_total == (FD_DP['number'] // FD_DP['dp_per_tag']) * 2:
            for indx in range(dp_number_total):
                x_tmp = int(dp_address_x_total[indx])
                y_tmp = int(dp_address_y_total[indx])

                if 4 <= x_tmp < w - 4:
                    idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, [x_tmp - 4, x_tmp - 2, x_tmp + 2, x_tmp + 4]])
                elif x_tmp < 4:
                    idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, [x_tmp + 2, x_tmp + 4, x_tmp + 6]])
                elif w - 4 < x_tmp <= w:
                    idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, [x_tmp - 2, x_tmp - 4, x_tmp - 6]])
        else:
            raise ValueError('Incorrect conversion of FD_DP address from Qsub and Qsum coordinate')

    # 补偿48M (Qsub) Qsub_adjoin_DP, HL_Single_DP, ZAF_DP, Neighbor_DP 在12M图像中
    dp_types = ['HL_Single_DP', 'ZAF_DP', 'Neighbor_DP']

    # for dp_type in dp_types:
    #     dp_number = decoded_dp[dp_type]['number']
    #     dp_address_x = decoded_dp[dp_type]['address_x']
    #     dp_address_y = decoded_dp[dp_type]['address_y']
    #
    #     dp_address_xy_total = np.unique(np.ceil(np.array([dp_address_x, dp_address_y]).T / 2), axis=0)
    #     dp_number_total = dp_address_xy_total.shape[0]
    #     if dp_number_total > 0:
    #         dp_address_x_total = dp_address_xy_total[:, 0].astype(int)
    #         dp_address_y_total = dp_address_xy_total[:, 1].astype(int)
    #
    #         if debug_flag:
    #             dp_type_total = [dp_type] * dp_number_total
    #             for i in range(dp_number_total):
    #                 dp_address_xy_total_all.append({
    #                     'dp_address_x_total': dp_address_x_total[i],
    #                     'dp_address_y_total': dp_address_y_total[i],
    #                     'dp_type_total': dp_type_total[i]
    #                 })
    #
    #         for indx in range(dp_number_total):
    #             x_tmp = dp_address_x_total[indx]
    #             y_tmp = dp_address_y_total[indx]
    #             # 对图像边缘进行处理
    #             if 4 <= x_tmp < w - 4:
    #                 idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, [x_tmp - 4, x_tmp - 2, x_tmp + 2, x_tmp + 4]])
    #             elif x_tmp < 4:  # 图像左边缘
    #                 idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, [x_tmp + 2, x_tmp + 4, x_tmp + 6]])
    #             elif w - 4 < x_tmp <= w:
    #                 idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, [x_tmp - 2, x_tmp - 4, x_tmp - 6]])

    # 补偿12M (Qsum) DP101_DP, DP1001_DP 在12M图像中

    dp_address_x_total = np.concatenate((DP101_DP['address_x'], DP1001_DP['address_x']))
    dp_address_y_total = np.concatenate((DP101_DP['address_y'], DP1001_DP['address_y']))
    dp_number_total = len(dp_address_x_total)

    if debug_flag:
        dp_type_total = ['DP101_DP'] * len(DP101_DP['address_x']) + ['DP1001_DP'] * len(DP1001_DP['address_x'])
        dp_address_xy_total_all.extend(zip(dp_address_x_total, dp_address_y_total, dp_type_total))

    for indx in range(dp_number_total):
        x_tmp = int(dp_address_x_total[indx])
        y_tmp = int(dp_address_y_total[indx])
        # 对图像边缘进行处理
        if x_tmp >= 4 and x_tmp < w - 3:
            idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, x_tmp-4:x_tmp+5:2])
        elif x_tmp < 4:  # 图像左边缘
            idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, x_tmp+2:x_tmp+7:2])
        elif x_tmp >= w - 3:  # 图像右边缘
            idraw_comp[y_tmp, x_tmp] = np.median(idraw[y_tmp, x_tmp-6:x_tmp-1:2])

    # 补偿12M (Qsum) 3px Cluster DP 在12M图像中
    dp_address_x_total = Cluster_DP['address_x']
    dp_address_y_total = Cluster_DP['address_y']
    dp_number_total = len(dp_address_x_total)

    if debug_flag:
        dp_type_total = ['CLUSTER_DP'] * dp_number_total
        dp_address_xy_total_all.extend(zip(dp_address_x_total, dp_address_y_total, dp_type_total))

    # 对补偿后的图像进行边缘填充
    idraw_comp_padded = np.pad(idraw_comp, ((2, 2), (2, 2)), 'edge')

    for indx in range(dp_number_total):
        x_tmp = int(dp_address_x_total[indx]) + 2
        y_tmp = int(dp_address_y_total[indx]) + 2
        # 使用中值滤波替换缺陷点
        idraw_comp[y_tmp-2, x_tmp-2] = np.median(idraw_comp_padded[y_tmp-2:y_tmp+3, x_tmp-2:x_tmp+3])

    return idraw_comp
