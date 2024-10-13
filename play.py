from ortools.sat.python import cp_model

# 定义一些辅助函数来处理索引转换和时间窗口约束
def time_window_constraint(model, ti, tj, yij, alpha_ij, d_i, L_i, U_i, T, M):
    if yij:
        model.Add(tj - ti >= alpha_ij - (1 - yij) * M)
        model.Add(ti - tj <= -alpha_ij + (1 - yij) * M)
        model.Add(ti - ti - 1 >= d_i - 1 + L_i - (1 - yij) * M)
        model.Add(ti - ti - 1 <= d_i - 1 + U_i + (1 - yij) * M)
        model.Add((ti + T) - ti - 1 >= d_i - 1 + L_i - yij * M)
        model.Add((ti + T) - ti - 1 <= d_i - 1 + U_i + yij * M)
    else:
        model.Add(ti - tj >= alpha_ij - (2 - yij) * M)
        model.Add(tj - ti <= -alpha_ij + (2 - yij) * M)
        model.Add(ti - ti - 1 >= d_i - 1 + L_i - (2 - yij) * M)
        model.Add(ti - ti - 1 <= d_i - 1 + U_i + (2 - yij) * M)
        model.Add((ti + T) - ti - 1 >= d_i - 1 + L_i - (1 - yij) * M)
        model.Add((ti + T) - ti - 1 <= d_i - 1 + U_i + (1 - yij) * M)

def hoist_assignment_constraint(model, zik, num_jobs, num_hoists):
    for job in range(num_jobs):
        model.Add(sum(zik[job][k] for k in range(num_hoists)) == 1)

def hoist_collision_constraint(model, zik, yij, num_jobs, num_hoists, M):
    for i in range(num_jobs - 1):
        for j in range(i + 1, num_jobs):
            for p in range(num_hoists):
                for q in range(num_hoists):
                    model.Add(tj - ti >= alpha_ij[p - q] - (3 - zik[i][p] - zik[j][q] - yij[i][j]) * M)
                    model.Add(ti - tj >= alpha_ij[q - p] - (2 - zik[i][p] - zik[j][q] + yij[i][j]) * M)

def main():
    # 创建CP-SAT模型
    model = cp_model.CpModel()

    # 假设一些参数，你需要根据实际案例调整这些参数
    num_jobs = 10  # 搬运作业数量
    num_hoists = 3  # Hoist数量
    T = model.NewIntVar(0, 1000, 'T')  # 周期长度
    ti = [model.NewIntVar(0, 1000, f'ti_{i}') for i in range(num_jobs)]
    zik = [[model.NewBoolVar(f'zik_{i}_{k}') for k in range(num_hoists)] for i in range(num_jobs)]
    yij = [[model.NewBoolVar(f'yij_{i}_{j}') for j in range(num_jobs)] for i in range(num_jobs)]

    # 设置一些虚拟的时间窗口和其他参数，实际需要根据具体问题设定
    d_i = [1 for _ in range(num_jobs)]
    L_i = [1 for _ in range(num_jobs)]
    U_i = [5 for _ in range(num_jobs)]
    alpha_ij = [[1 for _ in range(num_hoists)] for _ in range(num_jobs)]
    M = 100

    # 添加约束条件
    hoist_assignment_constraint(model, zik, num_jobs, num_hoists)
    for i in range(num_jobs - 1):
        for j in range(i + 1, num_jobs):
            time_window_constraint(model, ti[i], ti[j], yij[i][j], alpha_ij[i][j], d_i[i], L_i[i], U_i[i], T, M)
    hoist_collision_constraint(model, zik, yij, num_jobs, num_hoists, M)

    # 目标函数：最小化周期长度T
    model.Minimize(T)

    # 创建求解器并求解
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Solution found:')
        print(f'Optimal T: {solver.Value(T)}')
        for i in range(num_jobs):
            print(f'ti_{i} value: {solver.Value(ti[i])}')  # 获取ti的值
            for k in range(num_hoists):
                if solver.Value(zik[i][k]):
                    print(f'Job {i} is assigned to Hoist {k}')
    else:
        print('No solution found.')

if __name__ == '__main__':
    main()