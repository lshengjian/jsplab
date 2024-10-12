import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
colors = plt.cm.tab10.colors

def draw_timeway(title='demo',tank_positions=None,hoist_moves=None,lift_time=8.5,lower_time=11.5):
    if tank_positions is None:
        tanks = ['Tank 1', 'Tank 2', 'Tank 3', 'Tank 4', 'Tank 5']
        tank_positions = {tank: i+1 for i, tank in enumerate(tanks)}
    else:
        tanks=tuple(tank_positions.keys())
    if hoist_moves is None:
        hoists = ['Hoist 1', 'Hoist 2']
        # 定义天车在每个周期内的运动
        # 每个元素是一个列表，包含(起始槽, 目的槽, 开始时间, 结束时间, 是否载物)
        hoist_moves = {
            'Hoist 1': [('Tank 1', 'Tank 3', 0, 6, True), ('Tank 3', 'Tank 2', 6, 7, False),('Tank 2', 'Tank 2', 7, 10, False), ('Tank 2', 'Tank 4', 10, 26, True)],
            'Hoist 2': [('Tank 5', 'Tank 3', 24, 26, False), ('Tank 3', 'Tank 5', 26, 32, True)]
        }
    else:
        hoists=tuple(hoist_moves.keys())

    x2ts=defaultdict(list)
    for t,x in tank_positions.items():
        x2ts[x].append(t)
    for x,ts in x2ts.items():
        for i,t in  enumerate(ts):
            tank_positions[t]+=i*0.5
    # 设置图表
    
    fig, ax = plt.subplots(figsize=(8, 8))

    # 绘制槽
    for tank, pos in tank_positions.items():
        ax.text(-2, pos, tank, ha='right', va='center', fontsize=10)

    # 用于跟踪是否已添加图例标签
    hoist_legend = {hoist: False for hoist in hoists}

    # 绘制天车运动
    for hoist, moves in hoist_moves.items():
        color = colors[hoists.index(hoist)]
        for move in moves:
            start_tank,end_tank,start_time,end_time,had_load = move
            #end_time=start_time+duration
            start_pos = tank_positions[start_tank]
            end_pos = tank_positions[end_tank]
            
            # 绘制载物移动
            if had_load:
                # 载物上升
                ax.plot([start_time, start_time + lift_time], [start_pos, start_pos], color=color, linestyle='-')
                # 载物移动
                ax.plot([start_time + lift_time, end_time -lower_time], [start_pos, end_pos], color=color, linestyle='-')
                # 载物下降
                ax.plot([end_time -lower_time, end_time], [end_pos, end_pos], color=color, linestyle='-')
            else:
                # 空载移动
                ax.plot([start_time, end_time ], [start_pos, end_pos], color=color, linestyle='--')
            
            # 添加图例
            if not hoist_legend[hoist]:
                ax.plot([], [], color=color, linestyle='-', label=f'{hoist}')
                hoist_legend[hoist] = True

    # 设置图表参数
    ax.set_xlabel('Time')
    #ax.set_xticks(list(range(0,60,5)))
    ax.set_yticks([])
    ax.legend()
    ax.set_title(title)
    plt.savefig(f'results/{title}.jpg', format='jpg', bbox_inches='tight', dpi=300)
    plt.pause(5)