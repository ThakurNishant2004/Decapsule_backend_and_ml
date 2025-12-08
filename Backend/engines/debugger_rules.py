# backend/engines/debugger_rules.py
from typing import Dict, List, Any

def detect_common_array_bugs(code: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues = []

    # 1. Out-of-bounds
    for b in analysis.get("boundary_issues", []):
        issues.append({
            "type": "index_error",
            "detail": f"{b['variable']}[{b['index']}] is out of bounds for length {b.get('length','?')}.",
            "severity": "high"
        })

    # 2. Suspicious patterns like i <= len(arr)
    if "len(" in code and "<=" in code:
        issues.append({
            "type": "boundary_condition",
            "detail": "Possible off-by-one error: using <= with len(array). Use < instead.",
            "severity": "medium"
        })

    # 3. Missing base conditions in loops
    if "while" in code and "break" not in code:
        issues.append({
            "type": "potential_infinite_loop",
            "detail": "While loop has no break condition.",
            "severity": "low"
        })

    return issues


def detect_common_string_bugs(code: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues = []

    # substring out of bounds
    for b in analysis.get("boundary_issues", []):
        issues.append({
            "type": "string_index_error",
            "detail": f"String index {b.get('index')} is out of bounds.",
            "severity": "medium"
        })

    return issues


# This debugger identifies:

# Out-of-bounds

# Off-by-one

# Missing loop conditions

# Potential infinite loops

# String index errors