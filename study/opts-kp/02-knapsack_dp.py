def knapsack_dp(wt, val, W, n):
    dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, W + 1):
            if wt[i - 1] > w:
                dp[i][w] = dp[i - 1][w]
            else:
                dp[i][w] = max(val[i - 1] + dp[i - 1][w - wt[i - 1]], dp[i - 1][w])
    return dp[n][W]
weights = [2, 3, 4, 5]
values =  [3, 4, 5, 6]
W = 5
n = len(weights)
print(knapsack_dp(weights, values, W, n))  # 输出：7