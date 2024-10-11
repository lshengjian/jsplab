import random
import math

# 假设一些问题相关的参数
num_hoists = 3  # Hoist数量
num_tanks = 5  # 处理槽数量
min_processing_time = [10] * num_tanks  # 每个处理槽的最小加工时间
max_processing_time = [20] * num_tanks  # 每个处理槽的最大加工时间
handling_time = [2] * num_tanks  # 执行搬运作业所需时间
alpha_matrix = [[0] * num_tanks for _ in range(num_tanks)]  # 搬运作业优先级相关的最小时间间隔矩阵

# 粒子编码
def generate_particle():
    hoist_assignment = [random.randint(1, num_hoists) for _ in range(num_tanks)]
    priority_sequence = list(range(num_tanks))
    random.shuffle(priority_sequence)
    return hoist_assignment, priority_sequence

# 计算粒子的适应度（这里简化处理，实际需根据详细约束）
def fitness_function(particle):
    hoist_assignment, priority_sequence = particle
    # 检查可行性并计算适应度值
    # 这里是简化的逻辑，实际需要根据约束条件准确判断可行性
    is_feasible = True
    for i in range(len(priority_sequence) - 1):
        hoist_i = hoist_assignment[priority_sequence[i]]
        hoist_j = hoist_assignment[priority_sequence[i + 1]]
        if hoist_i == hoist_j:
            # 同一Hoist执行的相邻作业需要满足时间间隔约束
            if handling_time[priority_sequence[i]] + alpha_matrix[priority_sequence[i]][priority_sequence[i + 1]] > max_processing_time[priority_sequence[i]]:
                is_feasible = False
        else:
            # 不同Hoist执行的相邻作业需要满足移动和碰撞约束（简化处理）
            if handling_time[priority_sequence[i]] + alpha_matrix[priority_sequence[i]][priority_sequence[i + 1]] > max_processing_time[priority_sequence[i]]:
                is_feasible = False
    if is_feasible:
        return 0  # 可行解，适应度为0（可根据实际情况调整适应度计算方式）
    else:
        return 1  # 不可行解，适应度为1（这里简单区分可行与不可行）

# 粒子群算法类
class ParticleSwarmOptimizer:
    def __init__(self, population_size, num_iterations, c1, c2, w):
        self.population_size = population_size
        self.num_iterations = num_iterations
        self.c1 = c1
        self.c2 = c2
        self.w = w
        self.particles = [generate_particle() for _ in range(population_size)]
        self.velocities = [[0] * num_tanks for _ in range(population_size)]
        self.pbest = self.particles.copy()
        self.gbest = min(self.particles, key=lambda x: fitness_function(x))

    def update_velocities(self):
        for i in range(self.population_size):
            for j in range(num_tanks):
                r1 = random.random()
                r2 = random.random()
                cognitive_component = self.c1 * r1 * (self.pbest[i][0][j] - self.particles[i][0][j])
                social_component = self.c2 * r2 * (self.gbest[0][j] - self.particles[i][0][j])
                self.velocities[i][j] = self.w * self.velocities[i][j] + cognitive_component + social_component

    def update_positions(self):
        for i in range(self.population_size):
            for j in range(num_tanks):
                new_hoist_assignment = self.particles[i][0][j] + int(self.velocities[i][j])
                new_hoist_assignment = max(1, min(num_hoists, new_hoist_assignment))
                self.particles[i][0][j] = new_hoist_assignment
                # 这里没有对优先级序列进行更新，实际可能需要根据规则更新
                # 可以考虑类似于交叉变异的操作来更新优先级序列

    def optimize(self):
        for iteration in range(self.num_iterations):
            self.update_velocities()
            self.update_positions()
            for i in range(self.population_size):
                current_fitness = fitness_function(self.particles[i])
                if current_fitness < fitness_function(self.pbest[i]):
                    self.pbest[i] = self.particles[i]
                if current_fitness < fitness_function(self.gbest):
                    self.gbest = self.particles[i]
        return self.gbest

# 使用粒子群算法解决问题
population_size = 50
num_iterations = 100
c1 = 1.5
c2 = 1.5
w = 0.7
optimizer = ParticleSwarmOptimizer(population_size, num_iterations, c1, c2, w)
best_solution = optimizer.optimize()
print("Best solution:", best_solution)