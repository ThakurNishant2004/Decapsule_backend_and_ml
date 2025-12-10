# backend/engines/string_engine.py
from typing import Dict, Any, List
import re

def simulate_string_operations(code: str, s: str) -> Dict[str, Any]:
    """
    VERY simple regex-based extraction of string operations:
    - s[i]
    - s[i:j]
    - s.find()
    - s.count()
    """
    timeline = []
    issues = []

    # detect substring indexing
    matches = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\[(.*?)\]", code)

    for var, expr in matches:
        timeline.append({
            "variable": var,
            "expr": expr,
            "context": "substring/index access"
        })

        # boundary check if integer
        try:
            idx = eval(expr, {"__builtins__": {}}, {})
            if isinstance(idx, int):
                if idx < 0 or idx >= len(s):
                    issues.append({
                        "variable": var,
                        "index": idx,
                        "error": "String index out of bounds"
                    })
        except Exception:
            pass

    return {
        "timeline": timeline,
        "boundary_issues": issues
    }

def analyze_string_code(code: str, sample_string: str = "abcdefghij") -> Dict[str, Any]:
    """
    Wrapper for /process endpoint.
    If frontend does not provide an actual string,
    we use a default test string of length 10.
    """
    return simulate_string_operations(code, sample_string)

# This handles:

# ✔ s[i]
# ✔ s[i:j] (not executed, but detected)
# ✔ Range errors
# ✔ Timeline for your visualizer