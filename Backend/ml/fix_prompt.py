def make_fix_prompt(code: str, issues: list):
    return f"""
You are an expert software engineer. Improve the following code by fixing the issues.

### Original Code
{code}

### Issues detected
{issues}

### Instructions
- Return ONLY the fixed code.
- Do NOT include explanations.
- Fix syntax, logic, recursion, loops, variables, array boundaries, etc.
"""
