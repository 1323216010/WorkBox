import numpy as np

def calculate_r_squared(x, y):
    # 确保使用高精度的数据类型
    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)

    if x.shape[0] != y.shape[0]:
        raise ValueError("Input arrays should have the same number of samples.")

    if x.shape[0] < 2:
        raise ValueError("Not enough data points to perform regression.")

    if len(x.shape) == 1:
        x = x.reshape(-1, 1)

    X = np.c_[np.ones(x.shape[0]), x]

    beta = np.linalg.pinv(X.T @ X) @ X.T @ y

    b = beta[0]
    a = beta[1:]

    y_pred = X @ beta

    TSS = np.sum((y - np.mean(y)) ** 2)
    ESS = np.sum((y - y_pred) ** 2)

    # 添加一个检查来处理TSS接近0的情况
    epsilon = 1e-10
    if TSS < epsilon:
        r2 = 1
    else:
        r2 = 1 - (ESS / TSS)

    return r2, a, b
