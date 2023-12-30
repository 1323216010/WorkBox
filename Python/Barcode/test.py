def actuator_barcode():
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

    buildInfo_ActuatorSN = [
        0x46, 0x80, 0x39, 0x40, 0xa4, 0x01, 0x87, 0x24, 0x0c, 0xb9, 0x41, 0x20, 0xc2, 0x08, 0x76, 0x10, 0xaf, 0x65, 0x79, 0xf7, 0xd1
    ]

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
    strActuatorBarcode[11] = map_data[((buildInfo_ActuatorSN[9] << 4) & 0x70) + ((buildInfo_ActuatorSN[10] >> 4) & 0x0F)]
    strActuatorBarcode[12] = map_data[((buildInfo_ActuatorSN[10] << 3) & 0x78) + ((buildInfo_ActuatorSN[11] >> 5) & 0x07)]
    strActuatorBarcode[13] = map_data[((buildInfo_ActuatorSN[11] << 2) & 0x7C) + ((buildInfo_ActuatorSN[12] >> 6) & 0x03)]
    strActuatorBarcode[14] = map_data[((buildInfo_ActuatorSN[12] << 1) & 0x7E) + ((buildInfo_ActuatorSN[13] >> 7) & 0x01)]
    strActuatorBarcode[15] = map_data[buildInfo_ActuatorSN[13] & 0x7F]

    return ''.join(strActuatorBarcode)


if __name__ == "__main__":
    print(actuator_barcode())