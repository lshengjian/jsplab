import numpy as np
import torch
from torch.utils.data import DataLoader

# 天车参数
a1 = 1.0  # 加速度
a2 = 1  # 减速度
V = 1.0  # 稳定速度
max_dis = 20.0  # 最大位移

# 计算加速和减速阶段的时间
T1 = V / a1
T2 = V / a2
D1=0.5*a1*T1**2
D2=0.5*a2*T2**2
D=D1+D2

# 生成数据集
def generate_data(num_samples=1000):
    data = []
    for _ in range(num_samples):
        # 随机选择一个小于最大位移的位移
        dis = np.random.uniform(0.2, max_dis)
        # 如果位移小于临界位移
        if dis <= D:
            t1 = np.sqrt(2 * dis / (a1+a1**2/a2))
            t2=a1*t1/a2
            t=t1+t2
            v = a1 * t1
#       # 获得稳定速度
        else:
            sd=dis-D
            t = T1 + sd / V +T2
            v = V
        data.append([t, v, dis])
    return torch.tensor(data, dtype=torch.float32)

# # 生成数据集
train_data = generate_data(1000)
train_dataloader = DataLoader(train_data, batch_size=64, shuffle=True)

for idx,batch in enumerate(train_dataloader):
    print(f"{'*'*8} {idx+1} {'*'*8}")
    print(batch[:3].numpy())



