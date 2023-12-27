import cv2

# 读取图像
img_matrix = cv2.imread(r"C:\Users\pengcheng.yan\Desktop\sensor_size.bmp", cv2.IMREAD_COLOR)  # 替换为你的图像路径

# 注意：OpenCV默认以BGR格式读取图像，可能需要转换为RGB
img_matrix = cv2.cvtColor(img_matrix, cv2.COLOR_BGR2RGB)

temp = img_matrix.shape
print(img_matrix.shape)  # 输出矩阵的形状