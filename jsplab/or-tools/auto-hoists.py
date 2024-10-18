from ortools.sat.python import cp_model
from collections import defaultdict,namedtuple
import matplotlib.pyplot as plt
# 创建模型
model = cp_model.CpModel()
hoists_pos = defaultdict(list)
hoists_steps = defaultdict(list)
num_hoists=2
horizon=20
for t in range(horizon):
    for i in range(num_hoists):
        if t==0 or t==horizon-1:
            hoists_pos[0].append(model.new_constant(0))
            hoists_pos[1].append(model.new_constant(7))
        else:
            hoists_pos[i].append(model.NewIntVar(0, 9, f'x_{i}_{t}'))

model.add(hoists_pos[0][5]==3)
model.add(hoists_pos[1][5]==5)
model.add(hoists_pos[1][10]==3)
model.add(hoists_pos[0][14]==4)
# 添加安全距离约束
for t in range(horizon):
    for i in range(0,num_hoists):
        if i>0:
            model.add(hoists_pos[i][t]>hoists_pos[i-1][t]+1)
        if t>0:
            dx=model.NewIntVar(0,9,'')
            model.add_abs_equality(dx,hoists_pos[i][t-1]-hoists_pos[i][t])
            model.add(dx<=1)
            hoists_steps[i].append(dx)

cumulative_var = cp_model.LinearExpr.Sum(hoists_steps[0]+hoists_steps[1])
model.Minimize(cumulative_var)

# 创建求解器并求解模型
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 输出结果
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f'Objective value: {solver.ObjectiveValue()}')
    H1 = [solver.Value(pos) for pos in hoists_pos[0]]
    H2 = [solver.Value(pos) for pos in hoists_pos[1]]


    x = range(len(H1))
    plt.plot(x, H1, label='H1')
    plt.plot(x, H2, label='H2')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.xticks(range(0,20,2))
    plt.title('Visualization of Two Crane Positions')
    plt.legend()
    plt.show()
else:
    print('No solution found.')