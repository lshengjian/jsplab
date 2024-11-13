from ortools.linear_solver import pywraplp

# 槽的数量
n = 13
# 吊机的数量
m = 3
# 槽位置数据
w = [0, 6, 8, 10, 11, 14, 14, 16, 19, 22, 24, 26, 29]
# 处理阶段对应的槽编号
s = [0, 4, 5, 7, 6, 8, 9, 10, 11, 12, 1, 2, 3, 0]
# 处理时间下限
a = [120, 150, 90, 120, 90, 30, 60, 60, 45, 130, 120, 90, 30]
# 处理时间上限
b = [180, 200, 120, 180, 125, 40, 120, 120, 75, 180, 120, 120, 60]
# 拾取时间
mu = [10] * (n + 1)
# 放下时间
eta = [10] * (n + 1)
# 吊机速度
v = 0.5
# 空吊机最大速度
lambda_ = 0.8
# 吊机之间的安全距离
d = 1.5
# 轨道最左端位置
w_l = 0
# 轨道最右端位置
w_r = max(w)

# 计算移动时间
r = [mu[i] + abs(w[s[i + 1]] - w[s[i]]) / v + eta[i] for i in range(n)]
r.append(mu[n] + abs(w[s[0]] - w[s[n]]) / v + eta[n])

# 计算个体移动约束的参数
l_i = [max(m - (w_r - max(w[s[i]], w[s[(i + 1) % (n + 1)]])) // d, 1) for i in range(n + 1)]
u_i = [min(1 + (min(w[s[i]], w[s[(i + 1) % (n + 1)]])) // d, m) for i in range(n + 1)]


def calculate_alpha_ij(i, j, h):
    if h == 0:
        return r[i] + abs(w[s[j]] - w[s[i + 1]]) / lambda_
    elif h > 0:
        if max(w[s[i]], w[s[i + 1]]) + h * d <= min(w[s[j]], w[s[j + 1]]):
            return float('-inf')
        elif w[s[i]] < w[s[i + 1]] and w[s[j]] < w[s[i + 1]] + h * d:
            return r[i] + (w[s[i + 1]] + h * d - w[s[j]]) / lambda_
        elif w[s[i]] < w[s[i + 1]] and w[s[j]] > w[s[i + 1]] + h * d and w[s[j + 1]] < w[s[i + 1]] + h * d <= w[s[j]]:
            return r[i] - mu[j] - (w[s[j]] - (w[s[i + 1]] + h * d)) / v
        elif w[s[i]] > w[s[i + 1]] and w[s[j]] < w[s[j + 1]] and w[s[i + 1]] + h * d <= w[s[j]] < w[s[i]] + h * d:
            return mu[i] + (w[s[i]] + h * d - w[s[j]]) / v
        elif w[s[i]] > w[s[i + 1]] and w[s[j]] > w[s[j + 1]] and w[s[i + 1]] + h * d <= w[s[j + 1]] < w[s[i]] + h * d <= w[s[j]]:
            return mu[i] - (w[s[j]] - (w[s[i]] + h * d)) / v - mu[j]
        elif w[s[j]] >= w[s[i]] + h * d > w[s[i + 1]] + h * d > w[s[j + 1]]:
            return mu[i] + (w[s[i]] + h * d - w[s[j]]) / v + max(0, eta[i] - mu[i])
        elif w[s[i]] + h * d > w[s[j]] > w[s[j + 1]] >= w[s[i + 1]] + h * d:
            return mu[i] + (w[s[i]] + h * d - w[s[j]]) / v
        elif w[s[i]] + h * d > w[s[j]] >= w[s[i + 1]] + h * d > w[s[j + 1]]:
            return mu[i] + (w[s[i]] + h * d - w[s[j]]) / v + max(0, eta[i] - mu[j])
    else:  # h < 0
        if min(w[s[i]], w[s[i + 1]]) + h * d >= max(w[s[j]], w[s[j + 1]]):
            return float('-inf')
        elif w[s[i]] > w[s[i + 1]] and w[s[j]] > w[s[i + 1]] + h * d:
            return r[i] + (w[s[j]] - (w[s[i + 1]] + h * d)) / lambda_
        elif w[s[i]] > w[s[i + 1]] and w[s[j]] < w[s[j + 1]] and w[s[j]] <= w[s[i + 1]] + h * d < w[s[j + 1]]:
            return r[i] - mu[j] - (w[s[i + 1]] + h * d - w[s[j]]) / v
        elif w[s[i]] < w[s[i + 1]] and w[s[j]] > w[s[j + 1]] and w[s[i]] + h * d < w[s[j]] <= w[s[i + 1]] + h * d:
            return mu[i] + (w[s[j]] - (w[s[i]] + h * d)) / v
        elif w[s[i]] < w[s[i + 1]] and w[s[j]] < w[s[j + 1]] and w[s[j]] <= w[s[i]] + h * d < w[s[j + 1]] <= w[s[i + 1]] + h * d:
            return mu[i] - (w[s[i]] + h * d - w[s[j]]) / v - mu[j]
        elif w[s[j]] <= w[s[i]] + h * d < w[s[i + 1]] + h * d < w[s[i + 1]]:
            return mu[i] + (w[s[j]] - (w[s[i]] + h * d)) / v + max(0, eta[i] - mu[j])
        elif w[s[i]] + h * d < w[s[j]] < w[s[j + 1]] <= w[s[i + 1]] + h * d:
            return mu[i] + (w[s[j]] - (w[s[i]] + h * d)) / v
        elif w[s[i]] + h * d < w[s[j]] <= w[s[i + 1]] + h * d < w[s[j + 1]]:
            return mu[i] + (w[s[j]] - (w[s[i]] + h * d)) / v + max(0, eta[i] - mu[j])


# 创建求解器
solver = pywraplp.Solver.CreateSolver('SCIP')

# 定义变量
T = solver.IntVar(0, 300, 'T')
t = [solver.IntVar(0, 299, f't_{i}') for i in range(n + 1)]
z = [[solver.IntVar(0, 1, f'z_{i}_{k}') for k in range(round(l_i[i]), round(u_i[i]) + 1)] for i in range(n + 1)]
x = [[solver.IntVar(0, 1, f'x_{i}_{j}') for j in range(i + 1, n + 1)] for i in range(n)]
y = [[solver.IntVar(0, 1, f'y_{i}_{j}') for j in range(i + 1, n + 1)] for i in range(n)]

# 处理时间约束
for i in range(1, n + 1):
    solver.Add(a[i] + r[i - 1] - (1 - x[i - 1][i]) * solver.infinity() <= t[i] - t[i - 1])
    solver.Add(t[i] - t[i - 1] <= b[i] + r[i - 1] + (1 - x[i - 1][i]) * solver.infinity())
    solver.Add(a[i] + r[i - 1] - x[i - 1][i] * solver.infinity() <= T + t[i] - t[i - 1])
    solver.Add(T + t[i] - t[i - 1] <= b[i] + r[i - 1] + x[i - 1][i] * solver.infinity())

# 移动对约束
for i in range(n + 1):
    for j in range(i + 1, n + 1):
        for p in range(l_i[i], u_i[i] + 1):
            for q in range(l_i[j], u_i[j] + 1):
                h = q - p
                alpha_ij = calculate_alpha_ij(i, j, h)
                beta_ij = -calculate_alpha_ij(j, i, -h) if h!= 0 else -alpha_ij
                if h == 0:
                    solver.Add(t[j] - t[i] >= alpha_ij - (3 - z[i][p] - z[j][q] - x[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] <= beta_ij + (2 - z[i][p] - z[j][q] + x[i][j]) * solver.infinity())
                elif h > 0:
                    solver.Add(t[j] - t[i] >= alpha_ij - (3 - z[i][p] - z[j][q] - x[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] <= beta_ij + (2 - z[i][p] - z[j][q] + x[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] <= T + beta_ij + (3 - z[i][p] - z[j][q] - x[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] >= alpha_ij - T - (2 - z[i][p] - z[j][q] + x[i][j]) * solver.infinity())
                else:
                    solver.Add(t[j] - t[i] >= alpha_ij + T - (3 - z[i][p] - z[j][q] - y[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] <= T + beta_ij + (2 - z[i][p] - z[j][q] + y[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] <= beta_ij - T + (3 - z[i][p] - z[j][q] - y[i][j]) * solver.infinity())
                    solver.Add(t[j] - t[i] >= alpha_ij - T - (2 - z[i][p] - z[j][q] + y[i][j]) * solver.infinity())

# 吊机分配约束
for i in range(n + 1):
    solver.Add(sum(z[i][k] for k in range(l_i[i], u_i[i] + 1)) == 1)

# 时间范围约束
solver.Add(t[0] == 0)

# 变量范围约束
for i in range(n + 1):
    for k in range(l_i[i], u_i[i] + 1):
        solver.Add(z[i][k] == 0 or z[i][k] == 1)
    for j in range(i + 1, n + 1):
        solver.Add(x[i][j] == 0 or x[i][j] == 1)
        solver.Add(y[i][j] == 0 or y[i][j] == 1)

# 设置目标函数
solver.Minimize(T)

# 求解模型
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print('Optimal solution found:')
    print('T =', T.solution_value())
    for i in range(n + 1):
        for k in range(l_i[i], u_i[i] + 1):
            if z[i][k].solution_value() == 1:
                print(f'Move {i} is performed by hoist {k}')
else:
    print('The problem does not have an optimal solution.')