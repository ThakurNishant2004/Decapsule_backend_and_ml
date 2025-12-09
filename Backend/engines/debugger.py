def analyze_code_for_issues(code: str):
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
