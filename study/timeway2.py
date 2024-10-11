import matplotlib.pyplot as plt

# 假设最多有10个天车和相应的颜色
hoists = ['Hoist {}'.format(i+1) for i in range(10)]
colors = plt.cm.tab10.colors  # 使用tab10色谱，确保颜色的多样性

# 定义天车在每个周期内的运动
# 每个元素是一个列表，包含(起始槽, 目的槽, 开始时间, 移动时间, 是否载物)
hoist_moves = {
    'Hoist 1': [('Tank 1', 'Tank 2', 0, 5, True), ('Tank 2', 'Tank 3', 10, 5, False)],
    'Hoist 2': [('Tank 3', 'Tank 4', 5, 5, True), ('Tank 4', 'Tank 5', 15, 5, False)],
    'Hoist 3': [('Tank 5', 'Tank 1', 10, 5, True), ('Tank 1', 'Tank 2', 20, 5, False)],
    # 可以继续定义更多天车的运动...
}

# 设置图表
fig, ax = plt.subplots(figsize=(10, 6))  # 调整图表大小

# 绘制天车运动
for idx, (hoist, moves) in enumerate(hoist_moves.items()):
    for move in moves:
        start_tank, end_tank, start_time, move_duration, load = move
        start_pos, end_pos = idx, (idx + 1) % len(hoist_moves)  # 模拟槽位
        
        # 计算载物移动的开始和结束时间
        lift_time = 3  # 原地上升时间
        lower_time = 3  # 原地下降时间
        total_duration = lift_time + move_duration + lower_time
        
        # 绘制载物移动
        if load:
            # 载物上升
            ax.plot([start_time, start_time + lift_time], [start_pos, start_pos], color=colors[idx % 10], linestyle='-')
            # 载物移动
            ax.plot([start_time + lift_time, start_time + lift_time + move_duration], [start_pos, end_pos], color=colors[idx % 10], linestyle='-')
            # 载物下降
            ax.plot([start_time + lift_time + move_duration, start_time + total_duration], [end_pos, end_pos], color=colors[idx % 10], linestyle='-')
        else:
            # 空载移动
            ax.plot([start_time, start_time + move_duration], [start_pos, end_pos], color=colors[idx % 10], linestyle='--')

# 设置图表参数
ax.set_xlabel('Time')
ax.set_ylabel('Hoist Position')
ax.set_yticks(range(10))
ax.set_yticklabels(['Tank {}'.format(i+1) for i in range(10)])
ax.set_xlim(0, 25)
ax.set_ylim(-1, 10)
ax.invert_yaxis()  # 天车0在顶部
ax.set_title('Hoist Scheduling Diagram')

# 显示图表
plt.show()