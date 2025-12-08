def basic_debug(code: str):
    issues = []

    if "return n *" in code and "n == 0" not in code:
        issues.append({
            "issue": "Missing base case for n == 0",
            "severity": "high",
            "suggestion": "Add: if n == 0: return 1"
        })

    if "arr[i+1]" in code and "len(arr)-1" not in code:
        issues.append({
            "issue": "Possible out-of-bounds array access",
            "severity": "medium"
        })

    return {"bugs": issues}
