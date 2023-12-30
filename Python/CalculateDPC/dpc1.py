import numpy as np
import cv2
import struct
from pathlib import Path
import copy
from utils import save_range_to_csv, correct, read_raw_image

def get_map(file, dict1):
    print('file:', file)

    print('lightingMode:', dict1['lightingMode'])

    # 创建Path对象
    path = Path(file)

    IDraw = read_raw_image(file, dict1['sensor_size'][0])

    if 'nvm_data_path' in dict1:
        IDraw = correct(IDraw, dict1, path.stem)


    ID_delta = IDraw


    save_range_to_csv(ID_delta, dict1['points'][2], dict1['points'][3], dict1['points'][0], dict1['points'][1], dict1['csv_path'] + '/' + path.stem + '.csv')
