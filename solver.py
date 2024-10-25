from ortools.sat.python import cp_model
from collections import defaultdict,namedtuple
import matplotlib.pyplot as plt
from jsplab.conf.mhp import MultiHoistProblem
# 创建模型
model = cp_model.CpModel()
hoists_pos = defaultdict(list)
hoists_steps = defaultdict(list)
cfg=MultiHoistProblem('mhp/t4j2.csv')
UP=1
DOWN=1
print(cfg.min_offset,cfg.max_offset)
print(cfg.tank_offsets)



num_hoists=2
T=22
horizon=2*T
R=2
data=[
    [(0,0),(4,2),(11,0),(16,3)],
    [(0+T,3),(5+T,6),(11+T,2),(17+T,6)],
]
for t in range(horizon+1):
    for i in range(num_hoists):
        hoists_pos[i].append(model.NewIntVar(0, 9, f'x_{i}_{t}'))
for t in range(T):
    for i in range(num_hoists):
        model.add(hoists_pos[i][t]==hoists_pos[i][t+T])

model.add(hoists_pos[0][0]==hoists_pos[0][2*T])
model.add(hoists_pos[1][0]==hoists_pos[1][2*T])
for i in range(num_hoists):
    for d in data[i]:
        s=1 if i==0 else -1
        model.add(hoists_pos[i][d[0]]==d[1])
        model.add(hoists_pos[i][d[0]+R]==d[1])
        model.add(hoists_pos[i][d[0]+T*s]==d[1])
        model.add(hoists_pos[i][d[0]+R+T*s]==d[1])



# 添加安全距离约束
for t in range(horizon):
    for i in range(0,num_hoists):
        if i>0:
            model.add(hoists_pos[i][t]>=hoists_pos[i-1][t]+1)
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
    #plt.xticks(range(0,50,2))
    plt.title(f'T={T}')
    plt.legend()
    plt.show()
else:
    print('No solution found.')