import numpy as np
import cv2
import struct
from pathlib import Path
import copy
from utils import save_range_to_csv, correct

def get_map(file, dict1):
    # input
    DEF_MatlabHandleZeroSytle = True;

    DEF_DARK = False
    DEF_MFG = True

    if dict1['lightingMode'].upper() != "D50":
        DEF_DARK = True


    if dict1['mode'].upper() != 'MFG':
        DEF_MFG = False

    if DEF_DARK:
        print(
            'lightingMode: Dark')
    else:
        print('lightingMode: D50')

    print('file:', file)

    BorderWidth = 2
    BorderHeight = 2
    threshold_detectable = 32

    ladderPattern = 1
    pairPattern = 2
    rowPattern = 3
    featureThreshold = 36.5
    # end input

    # 创建Path对象
    path = Path(file)

    with open(file, 'rb') as f:
        img = f.read()  # 读取整个文件
    img_len = len(img)

    if dict1.get("program", "").lower() == "pit":
        w, h = dict1['sensor_size'][0], dict1['sensor_size'][1] + 40
        tt = struct.unpack('<' + str(w * h) + 'h', img)
        IDraw = np.array(tt).reshape((h, w))
        IDraw = IDraw[40:, :]
    elif dict1.get("program", "").lower() == "varo" and dict1.get("lightingMode", "dark").lower() == "dark":
        w, h = dict1['sensor_size'][0], dict1['sensor_size'][1] + 40
        tt = struct.unpack('<' + str(w * h) + 'h', img)
        IDraw = np.array(tt).reshape((h, w))
    else:
        w, h = dict1['sensor_size'][0], dict1['sensor_size'][1]
        tt = struct.unpack('<' + str(w * h) + 'h', img)
        IDraw = np.array(tt).reshape((h, w))



    if 'nvm_data_path' in dict1:
        IDraw = correct(IDraw, dict1, path.stem)

    imgWidth, imgHeight = dict1['sensor_size'][0], dict1['sensor_size'][1]

    # IDraw = focusGains_OCLHV_Comp(IDraw)
    pass
    # preprocess
    # input
    pedestal = -16
    signed = True
    AWB = True
    if DEF_DARK:
        AWB = False

    ID = (IDraw + pedestal).astype(np.float64)

    if not signed:
        ID[ID < 0] = 0
    if AWB:
        blockSizeR = 100
        blockSizeC = 100
        ID_plane = [None, None, None, None]
        ID_plane[0] = ID[0::2, 0::2]
        ID_plane[1] = ID[0::2, 1::2]
        ID_plane[2] = ID[1::2, 0::2]
        ID_plane[3] = ID[1::2, 1::2]
        centre = [h / 4, w / 4]
        balanceTemp = np.zeros((4,), dtype=np.float64)
        for i in range(4):
            balanceTemp[i] = np.mean(ID_plane[i][int(centre[0] - blockSizeR / 2): int(centre[0] + blockSizeR / 2),
                                     int(centre[1] - blockSizeC / 2): int(centre[1] + blockSizeC / 2)])
        balance = np.max(balanceTemp) / balanceTemp
        ID[0::2, 0::2] = balance[0] * ID_plane[0]
        ID[0::2, 1::2] = balance[1] * ID_plane[1]
        ID[1::2, 0::2] = balance[2] * ID_plane[2]
        ID[1::2, 1::2] = balance[3] * ID_plane[3]
        ID[ID > 1023] = 1023
    pass

    ID = np.round(ID)

    if dict1.get("output_raw", False) == True:
        save_range_to_csv(ID, dict1['points'][2], dict1['points'][3], dict1['points'][0], dict1['points'][1],
                          dict1['csv_path'] + '/' + path.stem + ' raw data.csv')


    roiSize = 15

    # 在所有边缘对 ID 进行对称填充
    pad_size = roiSize - 1
    ID_mirror = np.pad(ID, ((pad_size, pad_size), (pad_size, pad_size)), mode='symmetric')

    # 在填充区域内交换偶数/奇数行
    row_indices = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
    row_indices_end = [-13, -14, -11, -12, -9, -10, -7, -8, -5, -6, -3, -4, -1, -2]
    swap(ID_mirror, row_indices)
    swap(ID_mirror, row_indices_end)

    # 在填充区域内交换偶数/奇数列
    col_indices = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
    col_indices_end = [-13, -14, -11, -12, -9, -10, -7, -8, -5, -6, -3, -4, -1, -2]
    swap(ID_mirror.T, col_indices)
    swap(ID_mirror.T, col_indices_end)


    # intensive5
    ID_avg = np.zeros_like(ID)
    # ID_avg = np.zeros_like(ID_mirror)

    ##intensive6
    ID_delta = np.zeros_like(ID)
    # intensive3
    map_cluster = np.zeros((imgHeight, imgWidth), dtype=np.bool_)
    # intensive4
    map_LowContrast_defect = np.zeros((imgHeight, imgWidth), dtype=np.bool_)
    # intensive2
    map_defectLow = np.zeros((imgHeight, imgWidth), dtype=np.bool_)
    # intensive1
    map_defect = np.zeros((imgHeight, imgWidth), dtype=np.bool_)

    if DEF_MFG:
        DarkSliceLevel = 120;
        D50SliceLevel = 0.19
        threshold_defectLow = 0.19;
        print('Defective Pixel MFG Mode')
        print("DPC threshold_defectLow ", threshold_defectLow)
        print("DPC    threshold_defect D50 %f Dark %f " % (D50SliceLevel, DarkSliceLevel))
    else:
        DarkSliceLevel = 130;
        D50SliceLevel = 0.22;
        threshold_defectLow = 0.22;
        print('Defective Pixel OQC Mode')
        print("DPC threshold_defectLow ", threshold_defectLow);
        print("DPC    threshold_defect D50 %f Dark %f " % (D50SliceLevel, DarkSliceLevel))
    # C++ mirror() in VenusDefectivePixelsTest.cpp line 900
    # R=ch1; Gr=ch2; Gb=ch3; B=ch4;  r g g b
    lstFilter = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for ft in lstFilter:
        ch = ID[ft[1]::2, ft[0]::2]
        tapw = taph = 7  # ==29/2/2
        chMirror = np.pad(ch, (tapw, tapw), 'symmetric')
        RSmooth = MovingAverage(chMirror, 15, 15)
        # C++ defectValueInLightField() in VenusDefectivePixelsTest.cpp line 1749
        RValid = chMirror[7:-7, 7:-7]
        if DEF_DARK:
            DefectBayer = RValid - RSmooth
            map_defect_bayer = np.zeros(DefectBayer.shape, dtype=np.bool_)
            map_defect_bayer[np.abs(DefectBayer) > DarkSliceLevel] = True

        else:
            # assert ( np.all( RSmooth>0))

            tInValid = np.abs(RSmooth) < 1e-7
            DefectBayer = (RValid - RSmooth) / RSmooth
            if DEF_MatlabHandleZeroSytle:
                DefectBayer[tInValid] = 1e7
            else:
                DefectBayer[tInValid] = 0

            map_defect_bayer = np.zeros(DefectBayer.shape, dtype=np.bool_)
            map_defect_bayer[np.abs(DefectBayer) > D50SliceLevel] = True
            map_defectLow_bayer = np.zeros(DefectBayer.shape, dtype=np.bool_)
            map_defectLow_bayer[np.abs(DefectBayer) > threshold_defectLow] = True
            # intensive2
            map_defectLow[ft[1]::2, ft[0]::2] = map_defectLow_bayer
            # intensive4
            map_LowContrast_defect[ft[1]::2, ft[0]::2] = map_defectLow_bayer
        # dark and d50 common
        # detectCluster  in defectMap= cov_map_defect_bayer #
        # detectCluster( &this->map_cluster_bayer, &this->map_defect_bayer, false );
        limitClusterSize = 3
        kernel = np.array([[1, 1, 1], [1, 100, 1], [1, 1, 1]], dtype=np.int64)
        cov_map_defect_bayer = np.zeros(chMirror.shape, dtype=np.bool_)
        cov_map_defect_bayer[7:-7, 7:-7] = map_defect_bayer
        # mode='same'
        map_work = cv2.filter2D(np.uint8(cov_map_defect_bayer), cv2.CV_8U, np.int32(kernel),
                                borderType=cv2.BORDER_CONSTANT)
        map_tmp = np.zeros(map_work.shape, dtype=np.bool_)
        map_tmp[map_work >= (100 + limitClusterSize - 1)] = True

        map_process = cv2.filter2D(np.uint8(map_tmp), cv2.CV_8U, np.int32(kernel), borderType=cv2.BORDER_CONSTANT)
        map_tmp = np.zeros(map_work.shape, dtype=np.bool_)
        map_tmp[map_process >= 1] = True

        map_cluster_bayer = np.zeros(cov_map_defect_bayer.shape, dtype=np.bool_)
        map_cluster_bayer[np.logical_and(map_tmp, cov_map_defect_bayer)] = True
        map_cluster_bayer = map_cluster_bayer[7:-7, 7:-7]
        # end detectCluster
        # intensive3
        map_cluster[ft[1]::2, ft[0]::2] = map_cluster_bayer
        # intensive1
        map_defect[ft[1]::2, ft[0]::2] = map_defect_bayer
        ##intensive6
        ID_delta[ft[1]::2, ft[0]::2] = DefectBayer  # dark==DefectFull
        # intensive5
        ID_avg[ft[1]::2, ft[0]::2] = RSmooth

    # end  dd
    if not DEF_DARK:
        # mirrorMask()  should test from here 20200805
        LowContrast_work = np.zeros((imgHeight + 14 * 2, imgWidth + 14 * 2), dtype=np.bool_)
        LowContrast_work[14:-14, 14:-14] = map_defectLow
        # ClusterLow( CMask* pOut, CMask* pIn, CRect region )
        # pIn= LowContrast_work, pOut=map_clusterLow_work -no use
        limitClusterSize = 4
        kernel = np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 100, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
                          dtype=np.int64)
        # ==MATLAB conv2(mapTemp_cluster, clusterPattern, 'same');
        map_clusterLow_work = cv2.filter2D(np.uint8(LowContrast_work), cv2.CV_8U, np.int32(kernel),
                                           borderType=cv2.BORDER_CONSTANT)
        map_tmp_Cluster_Low = np.zeros(map_clusterLow_work.shape, dtype=np.bool_)
        map_tmp_Cluster_Low[map_clusterLow_work >= (100 + limitClusterSize - 1)] = True
        map_process_Cluster_Low = cv2.filter2D(np.uint8(map_tmp_Cluster_Low), cv2.CV_8U, np.int32(kernel),
                                               borderType=cv2.BORDER_CONSTANT)
        map_tmp_Cluster_Low = np.zeros(map_clusterLow_work.shape, dtype=np.bool_)
        map_tmp_Cluster_Low[np.logical_and(map_process_Cluster_Low, LowContrast_work)] = True

        map_clusterLow = map_tmp_Cluster_Low[14:-14, 14:-14]
        # end ClusterLow()
    map_defect_cluster_removed = np.array(map_defect)
    map_defect_cluster_removed[np.logical_and(map_defect_cluster_removed, map_cluster)] = False
    # detectDivide()
    map_border = np.array(map_defect_cluster_removed)
    map_border[BorderWidth:-BorderWidth, BorderHeight:-BorderHeight] = False

    map_detection = np.zeros((imgHeight, imgWidth), dtype=np.int64)
    defectPOS = np.nonzero(map_defect_cluster_removed)
    # map_detection is important!!!
    for y, x in zip(defectPOS[0], defectPOS[1]):
        neighbours = []
        center = 0
        for yy in [-2, 0, 2]:
            for xx in [-2, 0, 2]:
                px, py = x + xx, y + yy
                if px > -1 and px < imgWidth and py > -1 and py < imgHeight:
                    value = ID[py, px]
                    if xx == 0 and yy == 0:
                        center = value
                    else:
                        neighbours.append(value)
        # isDetectable
        tempNeighbour = abs(center - (sum(neighbours) - max(neighbours) - min(neighbours)) / (len(neighbours) - 2))
        if tempNeighbour > threshold_detectable:
            map_detection[y, x] = 3
        else:
            map_detection[y, x] = 1
    kernelPattern = 2
    if kernelPattern == pairPattern:
        kernel = np.array([[1, 0, 1, 0, 1], [0, 0, 0, 0, 0], [1, 0, 33, 0, 1], [0, 0, 0, 0, 0], [1, 0, 1, 0, 1]],
                          dtype=np.int64)
        map_pair = cv2.filter2D(np.uint8(map_detection), cv2.CV_8U, np.int32(kernel), borderType=cv2.BORDER_CONSTANT)

    # mapPair()
    map_DP = np.zeros((imgHeight, imgWidth), np.bool_)
    map_NDP = np.zeros((imgHeight, imgWidth), np.bool_)
    map_DPP = np.zeros((imgHeight, imgWidth), np.bool_)
    map_NDPP = np.zeros((imgHeight, imgWidth), np.bool_)
    map_DP[map_pair == 99] = True
    map_NDPP[map_pair == 34] = True
    map_NDP[map_pair == 33] = True
    map_DPP[np.logical_and(map_pair > 35, map_pair != 99)] = True
    kernelPattern = 1
    if kernelPattern == ladderPattern:
        kernel = np.array([[0, 1, 0, 1, 0], [0, 0, 0, 0, 0], [0, 1, 33, 1, 0], [0, 0, 0, 0, 0], [0, 1, 0, 1, 0]],
                          dtype=np.int64)
        map_ladder = cv2.filter2D(np.uint8(map_detection), cv2.CV_8U, np.int32(kernel), borderType=cv2.BORDER_CONSTANT)

    # mapLadder()
    map_DLP = np.zeros((imgHeight, imgWidth), np.bool_)
    map_NLP = np.zeros((imgHeight, imgWidth), np.bool_)
    map_DLP[np.logical_and(map_ladder > 35, map_ladder != 99)] = True
    map_NLP[map_ladder == 34] = True
    # mapRow()
    map_ARPD = np.zeros((imgHeight, imgWidth), np.bool_)
    map_ARPDLow = np.zeros((imgHeight, imgWidth), np.bool_)
    if not DEF_DARK:
        kernelPattern = 3
        if kernelPattern == rowPattern:
            kernel = np.array([[0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 33, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0]],
                              dtype=np.int64)
            map_row = cv2.filter2D(np.uint8(map_detection), cv2.CV_8U, np.int32(kernel), borderType=cv2.BORDER_CONSTANT)
        map_ARPD[np.logical_and(map_row > 33, map_row != 99)] = True

    # combine() 1
    mapFail_noFeature = np.zeros((imgHeight, imgWidth), np.int64)
    mapFail_noFeature[map_DP] = 1
    mapFail_noFeature[map_DPP] = 2
    mapFail_noFeature[map_border] = 3
    # mapFail_noFeature[map_feature] =4
    mapFail_noFeature[map_NDP] = 5
    mapFail_noFeature[map_NDPP] = 6
    if not DEF_DARK:
        mapFail_noFeature[map_clusterLow] = 7
    mapFail_noFeature[map_DLP] = 8
    mapFail_noFeature[map_NLP] = 9
    if not DEF_DARK:
        mapFail_noFeature[map_ARPD] = 10
    # mapFail_noFeature[map_ARPDLow] =11
    mapFail_noFeature[map_cluster] = 12
    # detectFeature()
    map_feature = np.zeros((imgHeight, imgWidth), np.bool_)
    map_featureScore = np.zeros((imgHeight, imgWidth), np.float64)
    # print('dpc_test_ver: 7.31')
    defectPOS = np.nonzero(np.logical_or(mapFail_noFeature == 1, mapFail_noFeature == 2))
    # map_detection is important!!!
    for y, x in zip(defectPOS[0], defectPOS[1]):
        neighbours = []
        center = 0
        for yy in [-2, -1, 0, 1, 2]:
            for xx in [-2, -1, 0, 1, 2]:
                px, py = x + xx, y + yy
                if px > -1 and px < imgWidth and py > -1 and py < imgHeight:
                    value = ID[py, px]
                    if xx == 0 and yy == 0:
                        center = value
                    else:
                        neighbours.append(value)
        # defectivePixel_featureScore_MI__Ver7p3__MI
        assert (len(neighbours) == 24)
        featPatt_dH = (((abs(neighbours[11] - neighbours[12])) / (30.0 / 7.0)) +
                       ((abs(neighbours[10] - neighbours[13])) / (30.0 / 5.0)) +
                       ((abs(neighbours[6] - neighbours[8])) / (30.0 / 3.0)) +
                       ((abs(neighbours[15] - neighbours[17])) / (30.0 / 3.0)) +
                       ((abs(neighbours[0] - neighbours[2])) / (30.0 / 2.0)) +
                       ((abs(neighbours[2] - neighbours[4])) / (30.0 / 2.0)) +
                       ((abs(neighbours[19] - neighbours[21])) / (30.0 / 2.0)) +
                       ((abs(neighbours[21] - neighbours[23])) / (30.0 / 2.0)) +
                       ((abs(neighbours[5] - neighbours[7])) / (30.0 / 1.0)) +
                       ((abs(neighbours[7] - neighbours[9])) / (30.0 / 1.0)) +
                       ((abs(neighbours[14] - neighbours[16])) / (30.0 / 1.0)) +
                       ((abs(neighbours[16] - neighbours[18])) / (30.0 / 1.0)));

        featPatt_dV = (((abs(neighbours[7] - neighbours[16])) / (30.0 / 7.0)) +
                       ((abs(neighbours[2] - neighbours[21])) / (30.0 / 5.0)) +
                       ((abs(neighbours[6] - neighbours[15])) / (30.0 / 3.0)) +
                       ((abs(neighbours[8] - neighbours[17])) / (30.0 / 3.0)) +
                       ((abs(neighbours[0] - neighbours[10])) / (30.0 / 2.0)) +
                       ((abs(neighbours[10] - neighbours[19])) / (30.0 / 2.0)) +
                       ((abs(neighbours[4] - neighbours[13])) / (30.0 / 2.0)) +
                       ((abs(neighbours[13] - neighbours[23])) / (30.0 / 2.0)) +
                       ((abs(neighbours[1] - neighbours[11])) / (30.0 / 1.0)) +
                       ((abs(neighbours[11] - neighbours[20])) / (30.0 / 1.0)) +
                       ((abs(neighbours[3] - neighbours[12])) / (30.0 / 1.0)) +
                       ((abs(neighbours[12] - neighbours[22])) / (30.0 / 1.0)));
        map_featureScore[y, x] = np.sqrt(featPatt_dH ** 2 + featPatt_dV ** 2)
        # end defectivePixel_featureScore_MI__Ver7p3__MI
        if map_featureScore[y, x] >= featureThreshold:
            print("[featureScore] detect x=%d,y=%d,featureScore=%.10f\n " % (x, y, map_featureScore[y, x]))
            map_feature[y, x] = True
    ####################
    # combine() 2  ,only use map_feature
    mapFail = np.array(mapFail_noFeature)
    mapFail[map_feature] = 4
    # calc count
    tx = []
    for i in range(12):
        tx.append(np.nonzero(mapFail == i + 1))

    lstDPTypeList = ["DP", "DPP", "border", "feature", "NDP", "NDPP", "clusterLow", "DLP", "NLP", "ARPD", "ARPDLow",
                     "cluster"]
    assert (len(lstDPTypeList) == 12)
    # print("for DPP,NDPP,DLP,NLP,ARPD,ARPDLow count, should div 2 ,so if you see 4 ,it is actually 2 ")
    dpc_defects_count = 0

    with open(dict1['log_path'] + '/' + path.stem + '.txt', 'w') as file:
        for i in range(12):
            dpc_defects_count += len(tx[i][0])
            str1 = "dpc_DP_count: ".replace('DP', lstDPTypeList[i]) + str(len(tx[i][0])) + ' '
            if len(tx[i][0]) > 0:
                str1 += str([(x, y) for y, x in zip(tx[i][0], tx[i][1])])
            # print(str1)
            file.write(str1 + '\n')

    # data_to_save = {}
    # types_to_save = dict1['fail'] # 举例，只保存这些类型
    # for i in range(12):
    #     if lstDPTypeList[i] in types_to_save:
    #         dpc_defects_count += len(tx[i][0])
    #         defect_list = [(int(x), int(y)) for y, x in zip(tx[i][0], tx[i][1])]
    #
    #         data_to_save[lstDPTypeList[i]] = {
    #             "count": len(tx[i][0]),
    #             "defects": defect_list
    #         }
    #
    # data_to_save["dpc_defects_count"] = dpc_defects_count
    #
    # # 将数据保存为JSON格式
    # with open(dict1['log_path'] + '/' + path.stem + '.json', 'w') as json_file:
    #     json.dump(data_to_save, json_file, indent=4)

    save_range_to_csv(ID_delta, dict1['points'][2], dict1['points'][3], dict1['points'][0], dict1['points'][1], dict1['csv_path'] + '/' + path.stem + '.csv')

    print('dpc_defects_count(total) ', dpc_defects_count)

# MovingAverage in VenusDefectivePixelsTest.cpp line 1675
def MovingAverage(inImage, tapWidth, tapHeight):
    MA_WINDOW_SIZE = tapWidth * tapHeight
    # note https://stackoverflow.com/questions/39457468/convolution-without-any-padding-opencv-python
    tKernel = (1.0 / MA_WINDOW_SIZE) * np.ones((tapHeight, tapWidth))
    out2 = cv2.filter2D(inImage, -1, tKernel)  # ==MATLAB 'symmetric', 'same'
    H = np.floor(np.array(tKernel.shape) / 2).astype(np.int64)
    out = out2[H[0]:-H[0], H[1]:-H[1]]

    return out

def focusGains_OCLHV_Comp(IDraw):
    w, h = IDraw.shape
    IDrawComp = copy.deepcopy(IDraw)
    IDrawComp = np.uint16(IDrawComp)
    halfW, halfH = int(w / 2), int(h / 2)
    halfHBin = int(halfH / 2)
    ROIsY, ROIsX = (187, 250)
    roiY, roiX = (16, 16)
    offsetY, offsetX = (17, 17)
    HLx, VTx = np.array([2, 2, 10, 10]) - 1, np.array([7, 7, 15, 15]) - 1
    HLy, VTy = np.array([3, 11, 3, 11]) - 1, np.array([6, 14, 6, 14]) - 1
    curRow, curCol = (17, 17)
    for curRow in range(17, 3009, 16):
        for curCol in range(17, 4017, 16):
            for X, Y in zip(HLx + curCol, HLy + curRow):
                IDrawComp[(Y, X)] = np.median([IDraw[(Y, X - 2)], IDraw[(Y, X + 2)], IDraw[(Y + 2, X)], IDraw[(Y - 2, X)]]) + 0.5000001
                IDrawComp[(Y, X + 1)] = np.median([IDraw[(Y, X - 1)], IDraw[(Y, X + 3)], IDraw[(Y + 2, X + 1)], IDraw[(Y - 2, X + 1)]]) + 0.5000001

            for X, Y in zip(VTx + curCol, VTy + curRow):
                IDrawComp[(Y, X)] = np.median([IDraw[(Y, X - 2)], IDraw[(Y, X + 2)], IDraw[(Y + 2, X)], IDraw[(Y - 2, X)]]) + 0.5000001
                IDrawComp[(Y + 1, X)] = np.median([IDraw[(Y + 1, X - 2)], IDraw[(Y + 1, X + 2)], IDraw[(Y - 1, X)], IDraw[(Y + 3, X)]]) + 0.5000001

    return IDrawComp

# 交换行或列
def swap(array, indices):
    for i in range(0, len(indices), 2):
        array[[indices[i], indices[i + 1]]] = array[[indices[i + 1], indices[i]]]