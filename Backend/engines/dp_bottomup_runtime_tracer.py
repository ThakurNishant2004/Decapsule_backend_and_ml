# def trace_dp_bottomup_runtime(code: str):
#     events = []

#     runtime_env = {
#         "__builtins__": {
#             "range": range,
#             "len": len,
#             "list": list,
#             "max": max,
#             "min": min,
#             "print": print,
#         }
#     }

#     try:
#         exec(code, runtime_env, runtime_env)

#         if "dp" not in runtime_env:
#             return [{"type": "dp_error", "error": "dp table not found"}]

#         dp = runtime_env["dp"]

#         if not isinstance(dp, list):
#             return [{"type": "dp_error", "error": "dp must be a list"}]

#         for i in range(len(dp)):
#             events.append({
#                 "type": "dp_row_complete",
#                 "row": i,
#                 "value": dp[i],
#                 "table": dp.copy()
#             })

#     except Exception as e:
#         return [{"type": "dp_error", "error": str(e)}]

#     return events


import ast

def trace_dp_bottomup_runtime(code: str, max_events: int = 300):
    """
    Bottom-Up DP Runtime Tracer
    ---------------------------
    - Executes user code safely
    - Tracks dp table row-by-row and cell-by-cell
    - Emits bounded visualization events
    """

    events = []

    # Restricted runtime
    runtime_env = {
        "__builtins__": {
            "range": range,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "sum": sum,
            "print": print,
        }
    }

    try:
        # 1️⃣ Execute user code
        exec(code, runtime_env, runtime_env)

        # 2️⃣ Validate dp table
        if "dp" not in runtime_env:
            return [{
                "type": "dp_error",
                "error": "dp table not found (bottom-up DP requires 'dp')"
            }]

        dp = runtime_env["dp"]

        if not isinstance(dp, list):
            return [{
                "type": "dp_error",
                "error": "dp must be a list for bottom-up DP visualization"
            }]

        # 3️⃣ Detect if dp is 1D or 2D
        is_2d = bool(dp) and isinstance(dp[0], list)

        # 4️⃣ Emit DP build start
        events.append({
            "type": "dp_init",
            "dimension": "2D" if is_2d else "1D",
            "rows": len(dp),
        })

        # 5️⃣ Emit table updates
        if not is_2d:
            # 🔹 1D DP
            for i in range(len(dp)):
                if len(events) >= max_events:
                    break

                events.append({
                    "type": "dp_update",
                    "row": i,
                    "value": dp[i],
                    "table": dp.copy()
                })

        else:
            # 🔹 2D DP
            for i in range(len(dp)):
                if len(events) >= max_events:
                    break

                for j in range(len(dp[i])):
                    if len(events) >= max_events:
                        break

                    events.append({
                        "type": "dp_update",
                        "row": i,
                        "col": j,
                        "value": dp[i][j],
                        "table": [r.copy() for r in dp]
                    })

                # Row completion marker
                events.append({
                    "type": "dp_row_complete",
                    "row": i,
                    "table": [r.copy() for r in dp]
                })

        # 6️⃣ Truncation notice
        if len(events) >= max_events:
            events.append({
                "type": "dp_truncated",
                "message": "DP visualization truncated to avoid excessive output"
            })

    except Exception as e:
        return [{
            "type": "dp_error",
            "error": str(e)
        }]

    return events
