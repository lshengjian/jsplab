from ortools.sat.python import cp_model

# 创建模型
model = cp_model.CpModel()


a = model.NewIntVar(10, 60, 'a')
b = model.NewIntVar(1, 10, 'q')
r = model.NewIntVar(0, 10, 'r')


model.add_modulo_equality(r,a,b)
model.maximize(r+b)

# 创建求解器并求解
solver = cp_model.CpSolver()

status = solver.Solve(model)
if status == cp_model.OPTIMAL:
    print('a =', solver.Value(a))
    print('b =', solver.Value(b))
    print('r =',  solver.Value(r))