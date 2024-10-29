from ortools.sat.python import cp_model

# 原始问题数据（示例数据，可根据实际情况修改）
n = 5  # 化学槽数量
m = 3  # 起重机数量
w = [0, 3, 5, 7, 2, 0]  # 槽的位置，包括加载/卸载站（w[0]和w[n+1]）
wr=max(w)
wl=min(w)
assert len(w) == n + 1, "w列表长度应等于n + 1"

a = [120, 150, 90, 120, 30]  # 每个阶段处理时间下限
b = [200, 200, 120, 180, 40]  # 每个阶段处理时间上限
mu = [8.5] * (n + 1)  # 拾取时间
eta = [11.5] * (n + 1)  # 放下载体时间
v = 1
lambda_ = 1
d = 1

# 计算一些辅助数据
r = [mu[i] + abs(w[i + 1] - w[i]) / v + eta[i] for i in range(n)]
M = 10000  # 一个足够大的数
d_value = 1 if d == 0 else d  # 避免除零错误
l=[]
u=[]
for i in range(n):
    w1=min(w[i], w[i + 1])
    w2=max(w[i], w[i + 1])
    l.append(max(m-(wr-w2)//d,1))
    u.append(min(1+(w1-wl)//d,m))

print("n:", n)
for i in range(n):
    print(f"m{i+1}: {l[i]}->{u[i]}")


def calculate_alpha_beta(h, i, j):
    if h == 0:
        if w[j] >= w[i + 1]:
            alpha_ij = r[i] + (w[j] - w[i + 1]) / lambda_
        else:
            alpha_ij = r[i] + (w[i + 1] - w[j]) / lambda_
        beta_ij = -r[j] - abs(w[j + 1] - w[i]) / lambda_
    elif h > 0:
        if max(w[i], w[i + 1]) + h * d <= min(w[j], w[j + 1]):
            alpha_ij = float('-inf')
        elif w[i] < w[i + 1] and w[j] < w[i + 1] + h * d:
            alpha_ij = r[i] + (w[i + 1] + h * d - w[j]) / lambda_
        elif w[i] < w[i + 1] and w[j] > w[j + 1] and w[j + 1] < w[i + 1] + h * d <= w[j]:
            alpha_ij = r[i] - mu[j] - (w[j] - (w[i + 1] + h * d)) / v
        elif w[i] > w[i + 1] and w[j] < w[j + 1] and w[i + 1] + h * d <= w[j] < w[i] + h * d:
            alpha_ij = mu[i] + (w[i] + h * d - w[j]) / v
        elif w[i] > w[i + 1] and w[j] < w[i + 1] + h * d:
            alpha_ij = mu[i] - (w[j] - (w[i] + h * d)) / v - mu[j]
        elif w[i] > w[i + 1] and w[j] > w[j + 1] and w[i + 1] + h * d <= w[j + 1] < w[i] + h * d <= w[j]:
            alpha_ij = mu[i] + (w[i] + h * d - w[j]) / v + max(0, eta[i] - mu[i])
        else:
            raise ValueError("Invalid case for alpha_ij calculation when h > 0")
        beta_ij = -calculate_alpha_beta(-h, j, i)
    elif h < 0:
        if min(w[i], w[i + 1]) + h * d >= max(w[j], w[j + 1]):
            alpha_ij = float('-inf')
        elif w[i] > w[i + 1] and w[j] > w[i + 1] + h * d:
            alpha_ij = r[i] + (w[j] - (w[i + 1] + h * d)) / lambda_
        elif w[i] > w[i + 1] and w[j] < w[j + 1] and w[j] <= w[i + 1] + h * d < w[j + 1]:
            alpha_ij = r[i] - mu[j] - (w[i + 1] + h * d - w[j]) / v
        elif w[i] < w[i + 1] and w[j] > w[j + 1] and w[i] + h * d < w[j] <= w[i + 1] + h * d:
            alpha_ij = mu[i] + (w[j] - (w[i] + h * d)) / v
        elif w[i] < w[i + 1] and w[j] > w[i + 1] + h * d:
            alpha_ij = mu[i] - (w[i] + h * d - w[j]) / v - mu[j]
        elif w[i] < w[i + 1] and w[j] < w[j + 1] and w[j] <= w[i] + h * d < w[j + 1] <= w[j + 1] - d:
            alpha_ij = mu[i] + (w[j] - (w[i] + h * d)) / v
        else:
            raise ValueError("Invalid case for alpha_ij calculation when h < 0")
        beta_ij = -calculate_alpha_beta(-h, j, i)
    return alpha_ij, beta_ij

# 创建模型
model = cp_model.CpModel()

# 定义变量
T = model.NewIntVar(0, 1000, 'T')
t = [model.NewIntVar(0, 1000, f't_{i}') for i in range(n + 1)]
z = [[model.NewIntVar(0, 1, f'z_{i}_{k}') for k in range(l[i], u[i] + 1)] if l[i] <= u[i] else [model.NewIntVar(0, 1, f'z_{i}_{k}') for k in range(0, 1)] for i in range(n )]
x = [[model.NewIntVar(0, 1, 'x_{}_{}'.format(i, j)) for j in range(i + 1, n + 1)] for i in range(n)]
y = [[model.NewIntVar(0, 1, 'y_{}_{}'.format(i, j)) for j in range(i + 1, n + 1)] for i in range(n)]
r = []
z=[]
for i in range(n):
    r_value = mu[i] + abs(w[i + 1] - w[i]) / v + eta[i]
    print(f"i: {i}, r[{i}]: {r_value}")
    r.append(r_value)

for i in range(n ):
    sub_z = []
    if l[i] <= u[i]:
        sub_z = [model.NewIntVar(0, 1, 'z_{}_{}'.format(i, k)) for k in range(l[i], u[i] + 1)]
        print(f"i: {i}, l[{i}]: {l[i]}, u[{i}]: {u[i]}, sub_z长度: {len(sub_z)}")
    else:
        sub_z = [model.NewIntVar(0, 1, 'z_{}_{}'.format(i, k)) for k in range(0, 1)]
        print(f"i: {i}, l[{i}] > u[{i}], 使用默认值, sub_z长度: {len(sub_z)}")
    z.append(sub_z)
# 添加约束
# 处理时间约束
for i in range(1, n ):
    model.Add(a[i] + r[i - 1] - (1 - x[i - 1, i]) * M <= t[i] - t[i - 1] <= b[i] + r[i - 1] + (1 - x[i - 1, i]) * M)
    model.Add(a[i] + r[i - 1] - x[i - 1, i] * M <= T + t[i] - t[i - 1] <= b[i] + r[i - 1] + x[i - 1, i] * M)

# 移动对约束
for i in range(n):
    for j in range(i + 1, n + 1):
        for p in range(l[i], u[i] + 1):
            for q in range(l[j], u[j] + 1):
                h = q - p
                alpha_ij, beta_ij = calculate_alpha_beta(h, i, j)
                if beta_ij <= 0 <= alpha_ij:
                    model.Add(t[j] - t[i] >= alpha_ij - (3 - z[i][p] - z[j][q] - x[i][j]) * M)
                    model.Add(t[j] - t[i] <= beta_ij + (2 - z[i][p] - z[j][q] + x[i][j]) * M)
                    model.Add(t[j] - t[i] <= T + beta_ij + (3 - z[i][p] - z[j][q] - x[i][j]) * M)
                    model.Add(t[j] - t[i] >= alpha_ij - T - (2 - z[i][p] - z[j][q] + x[i][j]) * M)
                elif beta_ij > 0:
                    model.Add(t[j] - t[i] <= beta_ij - T + (3 - z[i][p] - z[j][q] - y[i][j]) * M)
                    model.Add(t[j] - t[i] >= alpha_ij - T - (2 - z[i][p] - z[j][q] + y[i][j]) * M)
                elif alpha_ij < 0:
                    model.Add(t[j] - t[i] >= alpha_ij + T - (3 - z[i][p] - z[j][q] - y[i][j]) * M)
                    model.Add(t[j] - t[i] <= T + beta_ij + (2 - z[i][p] - z[j][q] + y[i][j]) * M)

# 其他约束
for i in range(n + 1):
    if l[i] <= u[i]:
        model.Add(sum(z[i][k] for k in range(l[i], u[i] + 1)) == 1)
    else:
        model.Add(sum(z[i][k] for k in range(0, 1)) == 1)  # 如果l[i]>u[i]，处理默认值情况
model.Add(t[0] == 0)
for i in range(1, n + 1):
    model.Add(0 < t[i] < T)

# 设置目标函数
model.Minimize(T)

# 求解模型
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 结果处理
if status == cp_model.OPTIMAL:
    print('Optimal cycle length:', solver.Value(T))
    for i in range(n + 1):
        for k in range(l[i], u[i] + 1):
            if l[i] <= u[i] and solver.Value(z[i][k]) == 1:
                print('Move m_{} is performed by hoist {}'.format(i, k))
else:
    print('No optimal solution found.')