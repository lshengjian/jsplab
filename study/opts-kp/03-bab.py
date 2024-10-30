import queue

# 物品类
class Item:
    def __init__(self, weight, value):
        self.weight = weight
        self.value = value

# 节点类
class Node:
    def __init__(self, level, profit, weight, bound):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound

# 计算上界
def bound(u, n, W, items):
    if u.weight >= W:
        return 0
    profit_bound = u.profit
    j = u.level + 1
    tot_weight = u.weight
    while j < n and tot_weight + items[j].weight <= W:
        tot_weight += items[j].weight
        profit_bound += items[j].value
        j += 1
    if j < n:
        profit_bound += (W - tot_weight) * (items[j].value / items[j].weight)
    return profit_bound

# 0-1背包分支定界算法
def knapsack_branch_and_bound(W, items):
    n = len(items)
    items.sort(key=lambda x: x.value / x.weight, reverse=True)

    Q = queue.Queue()
    u = Node(-1, 0, 0, 0)
    Q.put(u)
    max_profit = 0

    while not Q.empty():
        u = Q.get()
        if u.level == n - 1:
            continue
        v = Node(u.level + 1, u.profit + items[u.level + 1].value,
                 u.weight + items[u.level + 1].weight, 0)
        if v.weight <= W and v.profit > max_profit:
            max_profit = v.profit

        v.bound = bound(v, n, W, items)
        if v.bound > max_profit:
            Q.put(v)

        v = Node(u.level + 1, u.profit, u.weight, 0)
        v.bound = bound(v, n, W, items)
        if v.bound > max_profit:
            Q.put(v)

    return max_profit

# weights = [2, 3, 4, 5]
# values = [3, 4, 5, 6]
W = 5
items=[Item(2,3),Item(3,4),Item(4,5),Item(5,6)]
print(knapsack_branch_and_bound(W,items))  # 输出：7