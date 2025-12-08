def make_explain_prompt(code, trace):
    return f"""
You are an AI debugger professor. Explain this code line-by-line and based on the trace.

Code:
{code}

Trace:
{trace}

Explain simply and clearly.
"""
