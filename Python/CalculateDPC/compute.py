import numpy as np
from scipy.ndimage import convolve

def focusGains_OCL_Comp(IDraw):
    focusGain_rev = '6.0'
    inputParamaterSectionName = 'focusGain'
    bayerFormat = 'rggb'
    pedestal = -16
    bitDepth = 10
    roiSize = [16, 16]
    ROIs = [262, 197]
    offset = [17, 13]
    # Assuming inputParameters are defined elsewhere
    # inputParameters[inputParamaterSectionName]['medianArea']
    # inputParameters[inputParamaterSectionName]['outputNVM']
    Kernels = np.array([[4, 3], [12, 3], [4, 11], [12, 11]])

    h, w = IDraw.shape

    # Initial output image is a copy of the input image
    IDrawComp = np.copy(IDraw)

    # Extract shielded pixel information
    roiX, roiY = roiSize
    ROIsX, ROIsY = ROIs
    offsetX, offsetY = offset

    # Extract the focus pixels in the defined kernel
    CordsY, CordsX = Kernels[:, 0] - 1, Kernels[:, 1] - 1

    # Skip in 'unit cell' blocks starting at the offsets
    currentRow, currentCol = offsetY - 1, offsetX - 1

    for currentROIY in range(ROIsY):
        for currentROIX in range(ROIsX):
            # Calculate the L shielded pixels for the current ROI
            for i in range(len(CordsX)):
                X = currentCol + CordsX[i]
                Y = currentRow + CordsY[i]

                # focus gain compensation with boundary check
                ZAF_AVG_L = np.median([IDraw[Y, max(X-2, 0)], IDraw[Y, min(X+2, w-1)], IDraw[min(Y+2, h-1), X], IDraw[max(Y-2, 0), X]])
                IDrawComp[Y, X] = ZAF_AVG_L

                ZAF_AVG_R = np.median([IDraw[Y, max(X-1, 0)], IDraw[Y, min(X+3, w-1)], IDraw[min(Y+2, h-1), X+1], IDraw[max(Y-2, 0), X+1]])
                IDrawComp[Y, X+1] = ZAF_AVG_R

            # Advance to the next set of columns
            currentCol += roiX

        # Advance to the next set of rows
        currentRow += roiY
        # Reset the column to the initial offset for the new row
        currentCol = offsetX - 1

    # Clip to integer values
    IDrawComp = IDrawComp.astype(np.uint16)

    return IDrawComp

def focusGains_OCLHV_1p0_Comp(IDraw, inputParameters):
    # 设置焦点增益版本
    focusGain_rev = '1.3'

    # 焦点增益校准
    inputParameters['focusGain']['mFile'] = 'focusGains_OCL_HV_2p2'
    inputParameters['focusGain']['type'] = 'OCLHV'
    inputParameters['focusGain']['version'] = '2.2'
    inputParameters['focusGain']['roiSize'] = [16, 16]
    inputParameters['focusGain']['ROIs'] = [262, 187]
    inputParameters['focusGain']['offset'] = [17, 17]
    inputParameters['focusGain']['H_outputNVM'] = [[16, 6], [8, 6]]
    inputParameters['focusGain']['V_outputNVM'] = [[6, 16], [6, 8]]
    inputParameters['focusGain']['Kernels'] = np.array([[[4, 3], [12, 3], [4, 11], [12, 11]],
                                                        [[7, 8], [15, 8], [7, 16], [15, 16]]]).transpose(1, 2, 0)
    inputParameters['focusGain']['sensorMode'] = ['A1']

    inputParamaterSectionName = 'focusGain'

    roiSize = inputParameters[inputParamaterSectionName]['roiSize']
    ROIs = inputParameters[inputParamaterSectionName]['ROIs']
    offset = inputParameters[inputParamaterSectionName]['offset']
    Kernels = inputParameters[inputParamaterSectionName]['Kernels']

    FPCMode = ''

    h, w = IDraw.shape

    # 预处理，执行基准减法
    IDrawComp = IDraw.copy()

    # 提取屏蔽像素信息
    roiX, roiY = roiSize
    ROIsX, ROIsY = ROIs
    offsetX, offsetY = offset

    # 提取定义的内核中的焦点像素
    HL_CordsY = Kernels[:, 0, 0]
    HL_CordsX = Kernels[:, 1, 0]
    VT_CordsY = Kernels[:, 0, 1]
    VT_CordsX = Kernels[:, 1, 1]

    currentRow, currentCol = offsetY - 1, offsetX - 1

    for currentROIY in range(ROIsY):
        for currentROIX in range(ROIsX):
            # 计算当前 ROI 的 L/R OCL_H 像素和 Xtlk 像素
            for i in range(len(HL_CordsX)):
                X = currentCol + HL_CordsX[i] - 1
                Y = currentRow + HL_CordsY[i] - 1

                if FPCMode == 'mean':
                    # 平均值
                    ZAF_AVG_L = np.mean([IDraw[Y, X - 2], IDraw[Y + 2, X], IDraw[Y - 2, X]])
                else:
                    # 中值
                    ZAF_AVG_L = np.median([IDraw[Y, X - 2], IDraw[Y + 2, X], IDraw[Y - 2, X]])

                IDrawComp[Y, X] = ZAF_AVG_L

                if FPCMode == 'mean':
                    # 平均值
                    ZAF_AVG_R = np.mean([IDraw[Y, X + 3], IDraw[Y + 2, X + 1], IDraw[Y - 2, X + 1]])
                else:
                    # 中值
                    ZAF_AVG_R = np.median([IDraw[Y, X + 3], IDraw[Y + 2, X + 1], IDraw[Y - 2, X + 1]])

                IDrawComp[Y, X + 1] = ZAF_AVG_R

            # 计算当前 ROI 的 T/B OCL_V 像素和 Xtlk 像素
            for i in range(len(VT_CordsX)):
                X = currentCol + VT_CordsX[i] - 1
                Y = currentRow + VT_CordsY[i] - 1

                if FPCMode == 'mean':
                    # 平均值
                    ZAF_AVG_T = np.mean([IDraw[Y, X - 2], IDraw[Y, X + 2], IDraw[Y - 2, X]])
                else:
                    # 中值
                    ZAF_AVG_T = np.median([IDraw[Y, X - 2], IDraw[Y, X + 2], IDraw[Y - 2, X]])

                IDrawComp[Y, X] = ZAF_AVG_T

                if FPCMode == 'mean':
                    # 平均值
                    ZAF_AVG_B = np.mean([IDraw[Y + 1, X - 2], IDraw[Y + 1, X + 2], IDraw[Y + 3, X]])
                else:
                    # 中值
                    ZAF_AVG_B = np.median([IDraw[Y + 1, X - 2], IDraw[Y + 1, X + 2], IDraw[Y + 3, X]])

                IDrawComp[Y + 1, X] = ZAF_AVG_B

            # 转到下一列组
            currentCol += roiX

        # 转到下一行组
        currentRow += roiY
        # 列填充，回车
        currentCol = offsetX - 1

    IDrawComp = IDrawComp.astype(np.uint16)

    return IDrawComp

def rfpn_correction(IDraw_frameSet):
    test_ver = 1.7

    # Check if IDraw_frameSet is 2D or 3D and adjust accordingly
    if IDraw_frameSet.ndim == 2:
        h, w = IDraw_frameSet.shape
        IDraw_frameSet = np.expand_dims(IDraw_frameSet, axis=2)
        nFrames = 1
    else:
        h, w, nFrames = IDraw_frameSet.shape

    n_OBP_rows = 40
    n_rFPN = 16
    rFPN_rows = np.linspace(n_OBP_rows - n_rFPN, n_OBP_rows - 1, n_rFPN).astype(int)

    # Extract active array from frame set
    img_AA_frameSet = IDraw_frameSet[n_OBP_rows:, :, :]

    # Extract OBP rows from frame set
    OBP_frameSet = IDraw_frameSet[:n_OBP_rows, :, :]

    # Perform white pixel correction in OBP region
    for i in range(nFrames):
        OBP_temp = OBP_frameSet[rFPN_rows, :, i]
        row_list, col_list = np.where(OBP_temp > 20 + np.mean(OBP_temp))

        for j in range(len(row_list)):
            row = row_list[j]
            col = col_list[j]

            if col < 3:
                OBP_temp[row, col] = OBP_temp[row, col + 2]
            elif col > OBP_temp.shape[1] - 3:
                OBP_temp[row, col] = OBP_temp[row, col - 2]
            else:
                OBP_temp[row, col] = (OBP_temp[row, col - 2] + OBP_temp[row, col + 2]) / 2

        OBP_frameSet[-n_rFPN:, :, i] = OBP_temp

    # Extract lower rows used for rFPN correction
    ave_OBP = np.mean(OBP_frameSet, axis=2)
    ave_OBP_lower = ave_OBP[-n_rFPN:, :]

    # Split by channel (assume RGrGbB bayer pattern)
    img_OBP_R1 = ave_OBP_lower[::4, ::2]
    img_OBP_R2 = ave_OBP_lower[2::4, ::2]
    img_OBP_Gr1 = ave_OBP_lower[::4, 1::2]
    img_OBP_Gr2 = ave_OBP_lower[2::4, 1::2]
    img_OBP_Gb1 = ave_OBP_lower[1::4, ::2]
    img_OBP_Gb2 = ave_OBP_lower[3::4, ::2]
    img_OBP_B1 = ave_OBP_lower[1::4, 1::2]
    img_OBP_B2 = ave_OBP_lower[3::4, 1::2]

    # Get per channel correction values
    R1_corr = np.mean(img_OBP_R1)
    R2_corr = np.mean(img_OBP_R2)
    Gr1_corr = np.mean(img_OBP_Gr1)
    Gr2_corr = np.mean(img_OBP_Gr2)
    Gb1_corr = np.mean(img_OBP_Gb1)
    Gb2_corr = np.mean(img_OBP_Gb2)
    B1_corr = np.mean(img_OBP_B1)
    B2_corr = np.mean(img_OBP_B2)

    # Align to logic resolution 2^-5
    R1_corr = np.floor(R1_corr / 2**-5) * 2**-5
    R2_corr = np.floor(R2_corr / 2**-5) * 2**-5
    Gr1_corr = np.floor(Gr1_corr / 2**-5) * 2**-5
    Gr2_corr = np.floor(Gr2_corr / 2**-5) * 2**-5
    Gb1_corr = np.floor(Gb1_corr / 2**-5) * 2**-5
    Gb2_corr = np.floor(Gb2_corr / 2**-5) * 2**-5
    B1_corr = np.floor(B1_corr / 2**-5) * 2**-5
    B2_corr = np.floor(B2_corr / 2**-5) * 2**-5

    correction_matrix = np.zeros((h - n_OBP_rows, w, nFrames))

    correction_matrix[::4, ::2, :] = R1_corr
    correction_matrix[2::4, ::2, :] = R2_corr
    correction_matrix[::4, 1::2, :] = Gr1_corr
    correction_matrix[2::4, 1::2, :] = Gr2_corr
    correction_matrix[1::4, ::2, :] = Gb1_corr
    correction_matrix[3::4, ::2, :] = Gb2_corr
    correction_matrix[1::4, 1::2, :] = B1_corr
    correction_matrix[3::4, 1::2, :] = B2_corr

    IDcorrected_frameSet = img_AA_frameSet.astype(float) + 16 - correction_matrix

    output = {
        'R1_corr': R1_corr,
        'R2_corr': R2_corr,
        'Gr1_corr': Gr1_corr,
        'Gr2_corr': Gr2_corr,
        'Gb1_corr': Gb1_corr,
        'Gb2_corr': Gb2_corr,
        'B1_corr': B1_corr,
        'B2_corr': B2_corr,
        'test_ver': test_ver
    }

    return IDcorrected_frameSet


def get_NVMdefect_64byte_Page_Type(target_file_barcode, alldata):
    # 初始化 nvm_Data_fullread 为 64x256 的空列表
    nvm_Data_fullread = [[None for _ in range(256)] for _ in range(64)]
    barcode_position_xls = 0  # Python 中索引从 0 开始

    # 计算 alldata 的大小
    size_ndata = len(alldata)

    # 计算 NVM 标记缺陷位置
    for i in range(1, size_ndata):
        wanted_file_barcode = alldata[i][barcode_position_xls]

        if wanted_file_barcode == target_file_barcode:
            for kk in range((len(alldata[i]) - 1) // 4):
                for offset in range(4):
                    NVM_raw_data = alldata[i][barcode_position_xls + 1 + kk * 4 + offset]
                    for LL in range(16):
                        start_index = (LL + 1) * 2
                        hex_string = NVM_raw_data[start_index:start_index + 2]
                        try:
                            add_NVM_data_temp = int(hex_string, 16)
                        except ValueError:
                            # 如果字符串不是有效的十六进制数，可以跳过或用默认值替换
                            add_NVM_data_temp = 0  # 或者使用其他合适的默认值
                            temp = 0
                        nvm_Data_fullread[LL + offset * 16][kk] = add_NVM_data_temp

    return nvm_Data_fullread

def get_NVMdefect_64byte_Page_Type_PDX(target_file_barcode, alldata):
    # 初始化 nvm_Data_fullread 为 64x256 的空列表
    nvm_Data_fullread = [[None for _ in range(1024)] for _ in range(64)]
    barcode_position_xls = 0  # Python 中索引从 0 开始

    # 计算 alldata 的大小
    size_ndata = len(alldata)

    # 计算 NVM 标记缺陷位置
    for i in range(1, size_ndata):
        wanted_file_barcode = alldata[i][barcode_position_xls]

        if wanted_file_barcode == target_file_barcode:
            for kk in range((len(alldata[i]) - 1) // 4):
                for offset in range(4):
                    NVM_raw_data = alldata[i][barcode_position_xls + 1 + kk * 4 + offset]
                    for LL in range(16):
                        start_index = (LL + 1) * 2
                        hex_string = NVM_raw_data[start_index:start_index + 2]
                        try:
                            add_NVM_data_temp = int(hex_string, 16)
                        except ValueError:
                            # 如果字符串不是有效的十六进制数，可以跳过或用默认值替换
                            add_NVM_data_temp = 0  # 或者使用其他合适的默认值
                            temp = 0
                        nvm_Data_fullread[LL + offset * 16][kk] = add_NVM_data_temp

    return nvm_Data_fullread

def get_NVMdefect_64byte_Page_Type_IN(target_file_barcode, alldata):
    # 初始化 nvm_Data_fullread 为 64x256 的空列表
    nvm_Data_fullread = [[None for _ in range(96)] for _ in range(64)]
    barcode_position_xls = 0  # Python 中索引从 0 开始

    # 计算 alldata 的大小
    size_ndata = len(alldata)

    # 计算 NVM 标记缺陷位置
    for i in range(1, size_ndata):
        wanted_file_barcode = alldata[i][barcode_position_xls]

        if wanted_file_barcode == target_file_barcode:
            for kk in range((len(alldata[i]) - 1) // 4):
                for offset in range(4):
                    NVM_raw_data = alldata[i][barcode_position_xls + 1 + kk * 4 + offset]
                    for LL in range(16):
                        start_index = (LL + 1) * 2
                        hex_string = NVM_raw_data[start_index:start_index + 2]
                        try:
                            add_NVM_data_temp = int(hex_string, 16)
                        except ValueError:
                            # 如果字符串不是有效的十六进制数，可以跳过或用默认值替换
                            add_NVM_data_temp = 0  # 或者使用其他合适的默认值
                            temp = 0
                        nvm_Data_fullread[LL + offset * 16][kk] = add_NVM_data_temp

    return nvm_Data_fullread

