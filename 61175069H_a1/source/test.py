import numpy as np

# 原始列表
original_list = [[1, 0, 0], [0, 0, 1], [0, 1, 1]]

# 转换为NumPy数组
original_array = np.array(original_list)
original_array = original_array[:,:,np.newaxis]
original_array = np.repeat(original_array, 3, axis=2)
# 逻辑取反
flipped_array = np.logical_not(original_array).astype(int)

# 打印结果
print("Original Array:")
print(original_array)

print("\nFlipped Array:")
print(flipped_array)
