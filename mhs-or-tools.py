from ortools.linear_solver import pywraplp
mu = [1, 1, 1, 1, 1]
w = [0, 2, 4, 6, 8, 10]
v_value = 1
eta = [1, 1, 1, 1, 1]
s = [0, 1, 2, 3, 4]
def multi_hoist_scheduling():
    # 创建求解器
    solver = pywraplp.Solver.CreateSolver('CBC')

    # 问题参数（简化示例）
    n = 5  # 化学槽数量
    m = 2  # 提升机数量
    lambda_value = 1

    

    d = 1
    w_l = 0
    w_r = 10
    a = [5, 5, 5, 5, 5]
    b = [10, 10, 10, 10, 10]



    # 定义决策变量
    T = solver.NumVar(0, 9999, 'T')  # 周期长度
    
    z = [[solver.IntVar(0, 1, f'z_{i}_{k}') for k in range(m)] for i in range(n + 1)]
    x = [[solver.IntVar(0, 1, f'x_{i}_{j}') for j in range(i + 1, n + 1)] for i in range(n)]
    y = [[solver.IntVar(0, 1, f'y_{i}_{j}') for j in range(i + 1, n + 1)] for i in range(n)]
    t= [solver.NumVar(0, 9999, f't_{i}') for i in range(n + 1)]
    # 定义约束
    # 个体移动约束
    for i in range(n + 1):
        l_i = max(1, m - (w_r - max(w[s[i]], w[s[i + 1]])) // d)
        u_i = min(m, (1 + min(w[s[i]], w[s[i + 1]] - w_l)) // d)
        solver.Add(sum(z[i][k] for k in range(l_i, u_i)) == 1)
    for i in range(n):  # 这里将范围从n + 1改为n，避免最后一次迭代出现问题
        l_i = max(1, m - (w_r - max(w[s[i] if i < len(s) else 0], w[s[i + 1] if i + 1 < len(s) else 0])) // d)
        u_i = min(m, (1 + min(w[s[i] if i < len(s) else 0], w[s[i + 1] if i + 1 < len(s) else 0]] - w_l)) // d)
        solver.Add(sum(z[i][k] for k in range(l_i, u_i)) == 1)

    # 处理时间约束
    for i in range(1, n + 1):
        solver.Add(a[i - 1] + r(i - 1) - (1 - x[i - 1][i]) * solver.infinity() <= t[i] - t[i - 1])
        solver.Add(t[i] - t[i - 1] <= b[i - 1] + r(i - 1) + (1 - x[i - 1][i]) * solver.infinity())
        solver.Add(a[i - 1] + r(i - 1) - x[i - 1][i] * solver.infinity() <= T + t[i] - t[i - 1])
        solver.Add(T + t[i] - t[i - 1] <= b[i - 1] + r[i - 1] + x[i - 1][i] * solver.infinity())

    # 移动对约束（简化示例）
    for i in range(n):
        for j in range(i + 1, n + 1):
            for p in range(m):
                for q in range(m):
                    h = q - p
                    alpha, beta = calculate_alpha_beta(i, j, h, w, s, mu, eta, v_value, lambda_value, d)
                    if beta <= 0 <= alpha:
                        solver.Add(t[j] - t[i] >= alpha - (3 - z[i][p] - z[j][q] - x[i][j]) * solver.infinity())
                        solver.Add(t[j] - t[i] <= beta + (2 - z[i][p] - z[j][q] + x[i][j]) * solver.infinity())
                    elif beta > 0:
                        solver.Add(t[j] - t[i] <= beta - T + (3 - z[i][p] - z[j][q] - y[i][j]) * solver.infinity())
                        solver.Add(t[j] - t[i] >= alpha - T - (2 - z[i][p] - z[j][q] + y[i][j]) * solver.infinity())
                    elif alpha < 0:
                        solver.Add(t[j] - t[i] >= alpha + T - (3 - z[i][p] - z[j][q] - y[i][j]) * solver.infinity())
                        solver.Add(t[j] - t[i] <= T + beta + (2 - z[i][p] - z[j][q] + y[i][j]) * solver.infinity())

    # 目标函数
    solver.Minimize(T)

    # 求解
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Optimal solution found:')
        print('T =', T.value())
        for i in range(n + 1):
            print(f't_{i} =', t[i].value())
            for k in range(m):
                print(f'z_{i}_{k} =', z[i][k].value())
        for i in range(n):
            for j in range(i + 1, n + 1):
                print(f'x_{i}_{j} =', x[i][j].value())
                print(f'y_{i}_{j} =', y[i][j].value())
    else:
        print('No optimal solution found.')

def r(i):
    return mu[i] + abs(w[s[i + 1]] - w[s[i]]) / v_value + eta[i]

def calculate_alpha_beta(i, j, h, w, s, mu, eta, v, lambda_, d):
    # 简化的alpha和beta计算示例，仅处理h=0的情况
    if h == 0:
        alpha = r(i) + (w[s[j]] - w[s[i + 1]]) / lambda_
        beta = -r(j) - abs(w[s[j + 1]] - w[s[i]] ) / lambda_
    return alpha, beta

if __name__ == '__main__':
    multi_hoist_scheduling()