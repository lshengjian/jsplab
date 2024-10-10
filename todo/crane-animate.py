import matplotlib.pyplot as plt
import matplotlib.animation as animation


# 假设两个天车的初始轨迹数据，每个轨迹元素为 [(时间起点, 槽位起点), (时间终点, 槽位终点)]
crane1_trajectory = [((0, 1), (3, 1)), ((3, 1), (6, 2)), ((6, 2), (9, 2))]
crane2_trajectory = [((1, 3), (4, 3)), ((4, 3), (7, 1)), ((7, 1), (10, 1))]


def update(frame):
    if frame < len(crane1_trajectory) - 1:
        new_crane1_pos_start = crane1_trajectory[frame + 1][0]
        new_crane1_pos_end = crane1_trajectory[frame + 1][1]
        crane1_trajectory.append(((new_crane1_pos_start[0], new_crane1_pos_start[1]),
                                  (new_crane1_pos_end[0], new_crane1_pos_end[1])))
    if frame < len(crane2_trajectory) - 1:
        new_crane2_pos_start = crane2_trajectory[frame + 1][0]
        new_crane2_pos_end = crane2_trajectory[frame + 1][1]
        crane2_trajectory.append(((new_crane2_pos_start[0], new_crane2_pos_start[1]),
                                  (new_crane2_pos_end[0], new_crane2_pos_end[1])))

    ax.clear()
    plot_crane_trajectory(crane1_trajectory, 'Crane 1')
    plot_crane_trajectory(crane2_trajectory, 'Crane 2')
    ax.set_xlabel('Time')
    ax.set_ylabel('Slot')
    ax.set_title('Two Cranes TimeWay Diagram')
    ax.legend()
    ax.grid(True)


def plot_crane_trajectory(crane_trajectory, label):
    line_segments = []
    for i in range(len(crane_trajectory)):
        start_time, start_slot = crane_trajectory[i][0]
        end_time, end_slot = crane_trajectory[i][1]
        if i < len(crane_trajectory) - 1:
            line_style = '-' if crane_trajectory[i][0][1]!= 0 else '--'
        else:
            line_style = '--'
        line_segment, = ax.plot([start_time, end_time], [start_slot, end_slot],
                                linewidth=2, linestyle=line_style)
        line_segments.append(line_segment)
    return line_segments


fig, ax = plt.subplots()

line1 = plot_crane_trajectory(crane1_trajectory, 'Crane 1')
line2 = plot_crane_trajectory(crane2_trajectory, 'Crane 2')

ani = animation.FuncAnimation(fig, update, frames=10, interval=1000, repeat=False)
plt.show()
