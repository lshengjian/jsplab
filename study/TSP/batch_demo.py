import numpy as np

# 自定义函数，根据距离类型计算向量的距离
def custom_function(vector, distance_type):
    if distance_type == "manhattan":
        return np.sum(np.abs(vector))
    elif distance_type == "euclidean":
        return np.sqrt(np.sum(vector ** 2))
    else:
        raise ValueError("Unsupported distance type")

# 创建一个二维数组，每一行代表一个向量
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
# 定义距离类型常数
distance_type = "euclidean"  # 或者 "manhattan"

# 使用向量化操作批量处理所有向量，并传递距离类型常数
result = np.apply_along_axis(custom_function, axis=1, arr=arr, distance_type=distance_type)

print("处理后的结果：", result)
