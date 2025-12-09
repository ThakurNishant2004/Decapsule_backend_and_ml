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
import ast

# ------------------------------
# 1) DP SIMULATION (LIS EXAMPLE)
# ------------------------------

def simulate_lis_dp(arr: List[int]) -> Dict[str, Any]:
    """
    Simulate the classic O(n^2) LIS DP.
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
                    snapshots.append({
                        "i": i,
                        "j": j,
                        "old": old_value,
                        "new": dp[i],
                        "dp": dp[:],
                        "reason": f"arr[{j}] < arr[{i}] ({arr[j]} < {arr[i]}) => dp[{i}] = dp[{j}] + 1"
                    })
    return {"final_dp": dp, "snapshots": snapshots}



# -------------------------------------
# 2) DP STATIC ANALYZER (TOP DOWN / BOTTOM UP)
# -------------------------------------

class DPAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.dp_updates = []
        self.memo_calls = []
        self.memo_sets = []
        self.detected = None

    def visit_Subscript(self, node):
        try:
            name = node.value.id
            index = ast.unparse(node.slice)
        except:
            return

        if name == "dp":
            self.dp_updates.append({"index": index, "line": node.lineno})

        if name in ("memo", "cache"):
            self.memo_calls.append({"index": index, "line": node.lineno})

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Subscript):
            try:
                name = node.targets[0].value.id
                index = ast.unparse(node.targets[0].slice)
            except:
                return

            if name == "dp":
                self.detected = "bottom_up"
                self.dp_updates.append({
                    "index": index,
                    "value": ast.unparse(node.value),
                    "line": node.lineno
                })

            if name in ("memo", "cache"):
                self.detected = "top_down"
                self.memo_sets.append({
                    "index": index,
                    "value": ast.unparse(node.value),
                    "line": node.lineno
                })

        self.generic_visit(node)


def analyze_dp(code: str):
    tree = ast.parse(code)
    analyzer = DPAnalyzer()
    analyzer.visit(tree)

    if analyzer.detected == "bottom_up":
        return {
            "type": "dp_bottom_up",
            "dp_updates": analyzer.dp_updates
        }

    if analyzer.detected == "top_down":
        return {
            "type": "dp_top_down",
            "memo_calls": analyzer.memo_calls,
            "memo_sets": analyzer.memo_sets
        }

    return {
        "type": "none",
        "message": "No DP pattern detected."
    }
