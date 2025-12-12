# def make_fix_prompt(code: str, issues: list):
#     return f"""
# You are an expert software engineer. Improve the following code by fixing the issues.

# ### Original Code
# {code}

# ### Issues detected
# {issues}

# ### Instructions
# - Return ONLY the fixed code.
# - Do NOT include explanations.
# - Fix syntax, logic, recursion, loops, variables, array boundaries, etc.
# """

# ml/fix_prompt.py
def make_fix_prompt(code: str, issues: list = None, strict_code_only: bool = True):
    """
    Build a prompt that asks the model to return ONLY fixed code.
    - issues: optional list/dict describing detected issues (helps the model focus).
    - strict_code_only: if True, strongly enforce "only code" output.
    """
    issues_block = f"### Issues detected:\n{issues}\n\n" if issues else ""
    strict_note = (
        "IMPORTANT: Return ONLY the corrected source code with no surrounding text, "
        "explanations, or markdown. If you must mark changes, use inline comments in the code only."
    ) if strict_code_only else "Return the corrected source code. Explanations are optional."

    return f"""
SYSTEM: You are an expert software engineer and code fixer.

USER: Improve and fix the following code.

### Original Code:
{code}

{issues_block}
### Instructions:
- {strict_note}
- Fix syntax errors, logic bugs, off-by-one or index issues, missing base cases in recursion, infinite loops.
- Keep the original algorithm and variable names unless renaming is necessary for correctness.
- If you add or change behavior, keep the change minimal and safe.
- Preserve the input/output style so the code remains runnable by the sandbox.

END
"""
