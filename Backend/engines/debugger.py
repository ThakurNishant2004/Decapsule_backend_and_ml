# engines/debugger.py

def analyze_code_for_issues(code: str):
    """
    OLD FUNCTION — your original static analysis logic.
    Returns JUST a list.
    """
    issues = []

    if "return" in code and "if" not in code and "for" not in code:
        issues.append("Suspicious return statement without flow control.")

    if "arr[" in code and "len(" not in code:
        issues.append("Possible array index out of range.")

    if "while" in code and "break" not in code:
        issues.append("Possible infinite loop: while loop without break.")

    if "fact(" in code and "n == 0" not in code:
        issues.append("Recursion missing base case (n == 0).")

    return issues


def debug_code_static(code: str):
    """
    NEW WRAPPER — ensures /process gets clean JSON.
    Converts simple strings into structured issue objects.
    """
    raw = analyze_code_for_issues(code)
    
    structured = []

    for issue in raw:
        if "infinite loop" in issue:
            structured.append({
                "type": "infinite_loop",
                "detail": issue,
                "severity": "high"
            })
        elif "array index" in issue:
            structured.append({
                "type": "index_error",
                "detail": issue,
                "severity": "medium"
            })
        elif "base case" in issue:
            structured.append({
                "type": "missing_base_case",
                "detail": issue,
                "severity": "critical"
            })
        else:
            structured.append({
                "type": "general_warning",
                "detail": issue,
                "severity": "low"
            })

    return {
        "issues": structured
    }
