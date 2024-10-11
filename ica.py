import random
from jsplab.utils import load_data

tanks=load_data('epsp/tanks.csv').astype(int)
print(tanks[:,0:5])
times=load_data('epsp/free_move_times.csv').astype(int)
print(times[0:5,0:5])
num_hoists = 3  # Hoist数量
num_tanks = 13  # 处理槽数量
min_processing_time = tanks[2,:]  # 每个处理槽的最小加工时间
max_processing_time = tanks[3,:]   # 
offsets=list(tanks[0,:])
seq=list(tanks[1,:])+[0]
handling_time = [0] * num_tanks  # 执行搬运作业所需时间
for i in range(num_tanks):
    s1=seq[i]
    s2=seq[+1]
    handling_time[i]=times[s1,s2]+20
alpha_matrix = [[0] * num_tanks for _ in range(num_tanks)]  # 搬运作业优先级相关的最小时间间隔矩阵

# 染色体编码
def generate_chromosome():
    hoist_assignment = [random.randint(1, num_hoists) for _ in range(num_tanks)]
    priority_sequence = list(range(num_tanks))
    random.shuffle(priority_sequence)
    return hoist_assignment, priority_sequence

# 启发式评价函数
def evaluate_chromosome(chromosome):
    hoist_assignment, priority_sequence = chromosome
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

# 同化操作 - 交叉和变异
def assimilate(chromosome1, chromosome2):
    # 针对搬运作业优先关系序列的双点交叉
    new_priority_sequence1, new_priority_sequence2 = cross_priority_sequence(chromosome1[1], chromosome2[1])
    # 针对Hoist分配序列的单点交换交叉
    new_hoist_assignment1, new_hoist_assignment2 = cross_hoist_assignment(chromosome1[0], chromosome2[0])
    # 针对优先关系序列的变异
    mutated_priority_sequence1 = mutate_priority_sequence(new_priority_sequence1)
    mutated_priority_sequence2 = mutate_priority_sequence(new_priority_sequence2)
    # 针对Hoist分配序列的变异
    mutated_hoist_assignment1 = mutate_hoist_assignment(new_hoist_assignment1)
    mutated_hoist_assignment2 = mutate_hoist_assignment(new_hoist_assignment2)
    return (mutated_hoist_assignment1, mutated_priority_sequence1), (mutated_hoist_assignment2, mutated_priority_sequence2)

def cross_priority_sequence(sequence1, sequence2):
    point1 = random.randint(1, len(sequence1) - 2)
    point2 = random.randint(point1 + 1, len(sequence1) - 1)
    new_sequence1 = sequence1[:point1] + sequence2[point1:point2] + sequence1[point2:]
    new_sequence2 = sequence2[:point1] + sequence1[point1:point2] + sequence2[point2:]
    return new_sequence1, new_sequence2

def cross_hoist_assignment(assignment1, assignment2):
    point = random.randint(0, len(assignment1) - 1)
    new_assignment1 = assignment1[:point] + assignment2[point:]
    new_assignment2 = assignment2[:point] + assignment1[point:]
    return new_assignment1, new_assignment2

def mutate_priority_sequence(sequence):
    index1, index2 = random.sample(range(len(sequence)), 2)
    sequence[index1], sequence[index2] = sequence[index2], sequence[index1]
    return sequence

def mutate_hoist_assignment(assignment):
    index = random.randint(0, len(assignment) - 1)
    new_assignment = assignment[:index] + [random.randint(1, num_hoists)] + assignment[index + 1:]
    return new_assignment

# 不可行解修复策略
def repair_infeasible_solution(chromosome):
    hoist_assignment, priority_sequence = chromosome
    repaired_priority_sequence = priority_sequence.copy()
    # 这里是简化的修复逻辑，实际需要根据详细的修复策略实现
    for i in range(len(priority_sequence) - 1):
        hoist_i = hoist_assignment[priority_sequence[i]]
        hoist_j = hoist_assignment[priority_sequence[i + 1]]
        if hoist_i == hoist_j:
            # 同一Hoist执行的相邻作业需要满足时间间隔约束
            if handling_time[priority_sequence[i]] + alpha_matrix[priority_sequence[i]][priority_sequence[i + 1]] > max_processing_time[priority_sequence[i]]:
                # 尝试调整顺序以满足约束
                if i > 0:
                    if handling_time[priority_sequence[i - 1]] + alpha_matrix[priority_sequence[i - 1]][priority_sequence[i]] <= max_processing_time[priority_sequence[i]]:
                        repaired_priority_sequence[i], repaired_priority_sequence[i - 1] = repaired_priority_sequence[i - 1], repaired_priority_sequence[i]
                elif i < len(priority_sequence) - 2:
                    if handling_time[priority_sequence[i + 2]] + alpha_matrix[priority_sequence[i + 2]][priority_sequence[i + 1]] <= max_processing_time[priority_sequence[i]]:
                        repaired_priority_sequence[i], repaired_priority_sequence[i + 2] = repaired_priority_sequence[i + 2], repaired_priority_sequence[i]
    return hoist_assignment, repaired_priority_sequence

# 帝国主义竞争算法主函数
def imperialist_competitive_algorithm():
    population_size = 50
    num_imperialists = 5
    competition_probability = 0.1
    crossover_probability = 0.9
    mutation_probability = 0.1
    max_repair_cycles = 3

    population = [generate_chromosome() for _ in range(population_size)]
    imperialists = random.sample(population, num_imperialists)
    colonies = [chromosome for chromosome in population if chromosome not in imperialists]

    global_best_solution = None
    global_best_fitness = float('inf')

    for iteration in range(100):  # 迭代次数
        # 评价帝国
        for imperialist in imperialists:
            fitness = evaluate_chromosome(imperialist)
            if fitness < global_best_fitness:
                global_best_solution = imperialist
                global_best_fitness = fitness
        # 同化和竞争操作
        for imperialist in imperialists:
            colony = random.choice(colonies)
            assimilated_chromosomes = assimilate(imperialist, colony)
            new_colony1, new_colony2 = assimilated_chromosomes
            if evaluate_chromosome(new_colony1) < evaluate_chromosome(colony):
                colonies.remove(colony)
                colonies.append(new_colony1)
            if evaluate_chromosome(new_colony2) < evaluate_chromosome(colony):
                colonies.remove(colony)
                colonies.append(new_colony2)
        # 不可行解修复
        repaired_population = [repair_infeasible_solution(chromosome) if evaluate_chromosome(chromosome) == 1 else chromosome for chromosome in population]
        population = repaired_population

        if global_best_fitness == 0:  # 如果找到最优解，提前结束
            break

    return global_best_solution



if __name__ == "__main__":
    best_solution = imperialist_competitive_algorithm()
    print("Best solution:", best_solution)

