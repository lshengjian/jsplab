import math

# 定义节点类
class Node:
    def __init__(self, level, profit, weight, bound):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound

# 计算下界
def bound(node, n, W, val, wt, profit, level):
    if node.weight >= W:
        return 0
    if level >= n:
        return node.profit
    includeProfit = profit[level]
    includeWeight = wt[level]
    bound = node.bound + includeProfit
    if (W - node.weight) < includeWeight:
        bound = bound + (W - node.weight) * (val[level + 1] / wt[level + 1])
    else:
        bound = bound + (val[level + 1] - profit[level])
    return bound

# 递归函数来解0-1背包问题
def knapSack(W, val, wt, profit, n, level=0, node=None):
    if node is None:
        node = Node(level, 0, 0, 0)
    if node.level == n:
        return node
    if node.weight >= W:
        return node
    if node.bound >= profit[n-1]:
        return node
    # 创建left和right子节点
    leftChild = Node(node.level + 1, node.profit, node.weight + wt[node.level], 0)
    rightChild = Node(node.level + 1, node.profit, node.weight, 0)
    leftChild.bound = bound(leftChild, n, W, val, wt, profit, level)
    rightChild.bound = node.bound + profit[node.level]
    # 剪枝
    if leftChild.bound < rightChild.bound:
        rightChild = knapSack(W, val, wt, profit, n, node.level + 1, rightChild)
    else:
        leftChild = knapSack(W, val, wt, profit, n, node.level + 1, leftChild)
    node.bound = max(leftChild.bound, rightChild.bound)
    return node

# 测试数据
val = [60, 100, 120]
wt = [10, 20, 30]
W = 50
n = len(val)

# 计算最大利润
maxProfit = knapSack(W, val, wt, val, n)
print("The maximum profit is ", maxProfit.bound)