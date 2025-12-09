def make_explain_prompt(code, trace):
    return f"""
You are an expert AI debugger and DSA instructor.

Explain the following code with very clear reasoning.

### Code
{code}

### Runtime Trace (events)
{trace}

### Your Task
1. Give a short summary of what the code does.
2. Then explain line-by-line.
3. Use the trace to explain how variables change.
4. Point out any potential bugs.
5. Suggest improvements.

Return explanation in clean readable text.
"""
