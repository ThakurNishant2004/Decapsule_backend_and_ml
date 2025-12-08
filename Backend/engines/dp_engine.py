# # backend/engines/dp_engine.py

# import ast

# class DPTable:
#     def __init__(self, rows, cols, fill=0):
#         self.table = [[fill for _ in range(cols)] for _ in range(rows)]
#         self.snapshots = []  # list of states after each update

#     def set(self, r, c, value):
#         self.table[r][c] = value
#         # store a deep copy snapshot
#         snap = [row[:] for row in self.table]
#         self.snapshots.append({
#             "update": {"r": r, "c": c, "value": value},
#             "table": snap
#         })

#     def get_all_snapshots(self):
#         return self.snapshots


# def simulate_lis_dp(arr):
#     n = len(arr)
#     dp = [1] * n
#     snapshots = []

#     for i in range(n):
#         for j in range(i):
#             if arr[j] < arr[i]:
#                 old_value = dp[i]
#                 dp[i] = max(dp[i], dp[j] + 1)
#                 if dp[i] != old_value:
#                     snapshots.append({
#                         "i": i,
#                         "j": j,
#                         "dp": dp[:],  # copy
#                         "reason": f"a[{j}] < a[{i}] => update dp[{i}]"
#                     })

#     return {
#         "final_dp": dp,
#         "snapshots": snapshots
#     }

# backend/engines/dp_engine.py
from typing import List, Dict, Any

def simulate_lis_dp(arr: List[int]) -> Dict[str, Any]:
    """
    Simulate the classic O(n^2) LIS DP.
    Returns final dp array and a list of snapshots showing dp updates.
    Each snapshot is { "i": i, "j": j, "old": old_value, "new": new_value, "dp": dp_copy, "reason": str }
    """
    n = len(arr)
    if n == 0:
        return {"final_dp": [], "snapshots": []}

    dp = [1] * n
    snapshots: List[Dict[str, Any]] = []

    for i in range(n):
        for j in range(i):
            if arr[j] < arr[i]:
                old_value = dp[i]
                candidate = dp[j] + 1
                if candidate > dp[i]:
                    dp[i] = candidate
                    # record snapshot
                    snapshots.append({
                        "i": i,
                        "j": j,
                        "old": old_value,
                        "new": dp[i],
                        "dp": dp[:],  # shallow copy for snapshot
                        "reason": f"arr[{j}] < arr[{i}] ({arr[j]} < {arr[i]}) => dp[{i}] = dp[{j}] + 1"
                    })
    return {"final_dp": dp, "snapshots": snapshots}

