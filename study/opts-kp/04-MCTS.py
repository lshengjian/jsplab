import math
import random

# 物品类
class Item:
    def __init__(self, weight, value):
        self.weight = weight
        self.value = value

# 节点类
class Node:
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0
        self.selected_item = None
# 选择操作
def select(node, capacity, items):
    while node.children or (len(items) > node.visits and capacity > 0):
        if node.children:
            node = best_child(node)
            capacity -= node.selected_item.weight if node.selected_item else 0
        else:
            new_node = Node(parent=node)
            new_node.selected_item = items[node.visits]
            node.children.append(new_node)
            return new_node
    return node


# 扩展操作（这里在选择中已部分体现）

# 模拟操作
def simulate(node, capacity, items):
    total_value = 0
    remaining_items = items[node.visits:]
    remaining_capacity = capacity
    random.shuffle(remaining_items)
    for item in remaining_items:
        if item.weight <= remaining_capacity:
            total_value += item.value
            remaining_capacity -= item.weight
    return total_value


# 回溯操作
def backpropagate(node, value):
    while node:
        node.visits += 1
        node.value += value
        node = node.parent
# 选择最佳子节点（UCB1公式）
def best_child(node):
    C = math.sqrt(2)
    best_value = -float('inf')
    best_children = []
    for child in node.children:
        exploitation = child.value / child.visits
        exploration = math.sqrt(2 * math.log(node.visits) / child.visits)
        value = exploitation + C * exploration
        if value > best_value:
            best_value = value
            best_children = [child]
        elif value == best_value:
            best_children.append(child)
    return random.choice(best_children)


# MCTS解决01背包问题        
def mcts_knapsack(capacity, items, num_iterations=1000):
    root = Node()
    for _ in range(num_iterations):
        selected_node = select(root, capacity, items)
        value = simulate(selected_node, capacity, items)
        backpropagate(selected_node, value)
    best_path = []
    node = root
    while node.children:
        node = best_child(node)
        if node.selected_item:
            best_path.append(node.selected_item)
    return sum(item.value for item in best_path)

W = 5
items=[Item(2,3),Item(3,4),Item(4,5),Item(5,6)]
print(mcts_knapsack(W,items))  # 输出：7