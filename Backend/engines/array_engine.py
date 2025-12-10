# backend/engines/array_engine.py
from typing import List, Dict, Any
import re

def detect_dict_variables(code: str) -> List[str]:
    """
    Detect dictionary declarations like:
    seen = {}
    memo = {}
    freq = {}
    """
    matches = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{\s*\}", code)
    return list(set(matches))


def extract_array_variable_names(code: str, dict_vars: List[str]) -> List[str]:
    """
    Detect variable names used like arrays: arr[i].
    Excludes dictionary variables detected earlier.
    """
    matches = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[", code)
    arr_vars = set(matches)
    return [v for v in arr_vars if v not in dict_vars]


def simulate_array_operations(code: str, input_array: List[int]) -> Dict[str, Any]:
    """
    Parses array-like operations BUT ignores dictionary accesses.
    """
    dict_vars = detect_dict_variables(code)
    arr_vars = extract_array_variable_names(code, dict_vars)

    timeline = []
    boundary_issues = []

    # find all indexing expressions like X[expr]
    index_patterns = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*?)\]", code)

    for var, index_expr in index_patterns:
        if var not in arr_vars:
            # Skip dictionary accesses
            continue

        timeline.append({
            "variable": var,
            "index_expr": index_expr,
            "note": f"Accessing {var}[{index_expr}]"
        })

        # Evaluate index safely
        try:
            idx = eval(index_expr, {"__builtins__": {}}, {})
            if not isinstance(idx, int):
                raise Exception("Not an integer index")

            if idx < 0 or idx >= len(input_array):
                boundary_issues.append({
                    "variable": var,
                    "index": idx,
                    "error": "Index out of bounds",
                    "length": len(input_array)
                })

        except Exception:
            boundary_issues.append({
                "variable": var,
                "index": index_expr,
                "error": "Non-evaluable index or unsafe expression (array case)"
            })

    return {
        "timeline": timeline,
        "boundary_issues": boundary_issues,
        "var_names": arr_vars,
        "dict_vars": dict_vars
    }

def analyze_array_code(code: str, sample_input: List[int] = None) -> Dict[str, Any]:
    """
    Wrapper for /process endpoint.
    If frontend does not provide actual array input,
    we simulate with a placeholder array of size 10.
    """
    if sample_input is None:
        sample_input = list(range(10))

    return simulate_array_operations(code, sample_input)



# This engine:

# ✔ Extracts which variables are arrays
# ✔ Finds array accesses
# ✔ Makes a timeline
# ✔ Detects out-of-bounds
# ✔ Safely evaluates index expressions
# ✔ Provides structured JSON for your frontend