from ortools.sat.python import cp_model
from jsplab.utils import load_data


def multi_hoist_scheduling():
    model = cp_model.CpModel()
    tanks=load_data('epsp/tanks.csv').astype(int)
    #print(tanks[:,0:5])
    times=load_data('epsp/free_move_times.csv').astype(int)
    #print(times[0:5,0:5])
    num_hoists = 3  # Hoist数量
    num_tanks = 13  # 处理槽数量
    min_processing_time = tanks[2,:]  # 每个处理槽的最小加工时间
    max_processing_time = tanks[3,:]   # 
    offsets=list(tanks[0,:])
    seq=list(tanks[1,:])+[0]
    hts = [0] * num_tanks  # 执行搬运作业所需时间
    for i in range(num_tanks):
        s1=seq[i]
        s2=seq[i+1]
        hts[i]=times[s1,s2]+20
    # 设定搬运作业数量n和Hoist数量m
    n = num_tanks
    m = num_hoists

    # 设定周期长度的上限T，以及一个较大的正数M
    T = model.NewIntVar(0,220,'T')
    M = 1000

    # 设定每个处理阶段的时间下限a和上限b，以及移动时间r（这里简单设定为固定值）
    a = min_processing_time #[10] * n
    b = max_processing_time #[20] * n
    r = hts #[5] * n

    # 定义决策变量
    ti = [model.NewIntVar(0, 220, f't_{i}') for i in range(n)]
    zik = [[model.NewBoolVar( f'z_{i}_{k}') for k in range(m)] for i in range(n)]
    yij = [[model.NewBoolVar( f'y_{i}_{j}') for j in range(n)] for i in range(n)]
    # 添加约束条件
    # 搬运作业只能分配给一台Hoist
    for i in range(n):
        model.add(ti[i]<T)
        model.Add(sum(zik[i][k] for k in range(m)) == 1)


    # 任意两个搬运作业之间只有唯一一种优先关系
    for i in range(n ):
        for j in range(i+1, n):
            model.Add(yij[i][j] + yij[j][i] == 1)

    # 时间窗口约束
    for i in range(1, n):
        model.Add(a[i] + r[i - 1] - (1 - yij[i - 1][i]) * M <= ti[i] - ti[i - 1])
        model.Add(ti[i] - ti[i - 1] <= b[i] + r[i - 1] + (1 - yij[i - 1][i]) * M)
        model.Add(a[i] + r[i - 1] - yij[i - 1][i] * M <= T + ti[i] - ti[i - 1])
        model.Add(T + ti[i] - ti[i - 1] <= b[i] + r[i - 1] + yij[i - 1][i] * M)

    # Hoist移动轨迹相关约束
    for i in range(n):
        for j in range(i + 1, n):
            for p in range(m):
                for q in range(p,m):
                    si1=seq[i]
                    si2=seq[i+1]
                    sj=seq[j]
                    h=q-p
                    model.Add(ti[j] - ti[i] >= abs(offsets[si2]-offsets[sj]) - M * (3 - zik[i][p] - zik[j][q] - yij[i][j]))
                    model.Add(ti[i] - ti[j] >= abs(offsets[si1]-offsets[sj]) - M * (2 - zik[i][p] - zik[j][q] + yij[i][j]))
                    model.Add(ti[i]+T - ti[i] >=abs(offsets[si1]-offsets[sj]) - M * (2 - zik[i][p] - zik[j][q] ))


    # 定义目标函数
    model.Minimize(T)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('最优解找到：')
        for i in range(n):
            print(f't_{i} = {solver.Value(ti[i])}')
            for k in range(m):
                if solver.Value(zik[i][k]):
                    print(f'move {i} by H{k+1}')

    else:
        print('未找到最优解')

if __name__ == "__main__":
    multi_hoist_scheduling()