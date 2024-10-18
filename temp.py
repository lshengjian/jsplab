from ortools.sat.python import cp_model

# 创建模型
model = cp_model.CpModel()

# 定义变量数组
num_vars = 5
vars = [model.NewIntVar(0, 10, f'var_{i}') for i in range(num_vars)]

# 定义累计变量
cumulative_var = cp_model.LinearExpr.Sum(vars)

# 添加约束条件（例如：累计变量小于等于某个值）
model.Add(cumulative_var <= 25)

# 定义目标函数（例如：最大化累计变量）
model.Maximize(cumulative_var)

# 创建求解器并求解模型
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 输出结果
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f'Objective value: {solver.ObjectiveValue()}')
    for var in vars:
        print(f'{var.Name()} = {solver.Value(var)}')
else:
    print('No solution found.')