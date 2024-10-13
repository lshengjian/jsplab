from ortools.sat.python import cp_model

# 定义天车移动范围和作业时间范围
range_trolley1 = range(0, 5)
range_trolley2 = range(1, 7)
wash_time_range1 = range(10, 61)
electroplate_time_range = range(30, 36)
wash_time_range2 = range(20, 41)

# 创建模型
model = cp_model.CpModel()

# 定义变量
trolley1_positions = [model.NewIntVar(0, 4, f'trolley1_pos_{i}') for i in range(5)]
trolley2_positions = [model.NewIntVar(1, 6, f'trolley2_pos_{i}') for i in range(5)]
wash_time1 = model.NewIntVar(10, 60, 'wash_time1')
electroplate_time = model.NewIntVar(30, 35, 'electroplate_time')
wash_time2 = model.NewIntVar(20, 40, 'wash_time2')

# 约束天车之间间隔至少1米
for i in range(5):
    model.Add(trolley2_positions[i] - trolley1_positions[i] >= 1)

# 定义目标变量（周期时间）
cycle_time = model.NewIntVar(0, 1000, 'cycle_time')
model.AddMaxEquality(cycle_time, [
    # 天车1的时间计算
    4 +  # 上料提升时间
    sum([model.NewIntVar(0, 4, f'trolley1_move_dist_{i}') for i in range(4)]) +  # 移动时间
    6,  # 下料放下时间
    # 天车2的时间计算
    wash_time1 + 
    2 * model.NewIntVar(0, 5, f'trolley2_move_dist_1') +  # 移动到电镀位
    electroplate_time + 
    2 * model.NewIntVar(0, 5, f'trolley2_move_dist_2') +  # 移动回水洗位
    wash_time2
])

# 约束天车的空载时间以避免碰撞
for i in range(4):
    # 天车1在移动到下一个位置前必须等待天车2离开
    model.Add(trolley1_positions[i + 1] >= trolley2_positions[i])
    # 天车2在移动到下一个位置前必须按地等待天车1离开
    model.Add(trolley2_positions[i + 1] >= trolley1_positions[i])

# 为移动距离变量添加绝对值约束
trolley1_move_dist_vars = [model.NewIntVar(0, 4, f'trolley1_move_dist_{i}') for i in range(4)]
for i in range(4):
    model.add_abs_equality(trolley1_move_dist_vars[i], trolley1_positions[i] - trolley1_positions[i + 1])
trolley2_move_dist_vars = [model.NewIntVar(0, 5, f'trolley2_move_dist_{i}') for i in range(2)]
for i in range(2):
    if i == 0:
        model.add_abs_equality(trolley2_move_dist_vars[i], trolley2_positions[i] - trolley2_positions[i + 1])
    else:
        model.add_abs_equality(trolley2_move_dist_vars[i], trolley2_positions[i + 1] - trolley2_positions[i])

# 创建求解器并求解
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f'Cycle Time: {solver.Value(cycle_time)}')
    print('Trolley 1 Positions:', [solver.Value(pos) for pos in trolley1_positions])
    print('Trolley 2 Positions:', [solver.Value(pos) for pos in trolley2_positions])
    print(f'Wash Time 1: {solver.Value(wash_time1)}')
    print(f'Electroplate Time: {solver.Value(electroplate_time)}')
    print(f'Wash Time 2: {solver.Value(wash_time2)}')
else:
    print('No solution found.')