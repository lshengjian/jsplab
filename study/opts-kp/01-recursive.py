def knapsack_recursive(weights, values, W, n):
    rt=0
    if n == 0 or W == 0:
        pass
    elif weights[n-1] > W:
        rt= knapsack_recursive(weights, values, W, n-1)
    else:
        rt1=values[n-1] + knapsack_recursive(weights, values, W-weights[n-1], n-1)
        rt2=knapsack_recursive(weights, values, W, n-1)
        print(f"{' '*2*(n-1)} ? {rt1} {rt2}")
        rt= max(rt1,rt2)
    print(f"{' '*2*n}{W}->{rt}")
    return rt

weights = [2, 3, 4, 5]
values =  [3, 4, 5, 6]
W = 5
n = len(weights)
print(knapsack_recursive(weights, values, W, n))  # 输出：7