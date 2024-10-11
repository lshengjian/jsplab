import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 设置槽位1和槽位2的位置
position1 = 0
position2 = 10

# 设置天车移动的时间
t_lift = 3  # 从槽位1提起物料的时间
t_move = 5  # 从槽位1移动到槽位2的时间
t_lower = 3  # 在槽位2放下物料的时间
t_return = 5  # 空载返回起始位置的时间

# 总时间
total_time = t_lift + t_move + t_lower + t_return

# 创建时间数组
t = np.linspace(0, total_time, 1000)

# 定义天车在每个阶段的位置
def position(t):
    if t < t_lift:
        return position1
    elif t < t_lift + t_move:
        return position1 + (position2 - position1) * (t - t_lift) / t_move
    elif t < t_lift + t_move + t_lower:
        return position2
    else:
        return position2 - (position2 - position1) * (t - (t_lift + t_move + t_lower)) / t_return

# 设置图形
fig, ax = plt.subplots()
line, = ax.plot([], [], 'bo-', lw=2)  # 天车位置
ax.set_xlim(0, position2)
ax.set_ylim(0, 1)
ax.set_title('天车调度模拟')
ax.set_xlabel('槽位位置')
ax.set_ylabel('天车')

# 初始化函数
def init():
    line.set_data([], [])
    return line,

# 动画更新函数
def update(frame):
    x = [position(t[i]) for i in range(len(t))]
    y = [0] * len(t)  # 天车高度固定
    line.set_data(x, y)
    return line,

# 创建动画
ani = animation.FuncAnimation(fig, update, frames=len(t), init_func=init, blit=True)

plt.show()