# def make_explain_prompt(code, trace):
#     return f"""
# You are an expert AI debugger and DSA instructor.

# Explain the following code with very clear reasoning.

# ### Code
# {code}

# ### Runtime Trace (events)
# {trace}

# ### Your Task
# 1. Give a short summary of what the code does.
# 2. Then explain line-by-line.
# 3. Use the trace to explain how variables change.
# 4. Point out any potential bugs.
# 5. Suggest improvements.

# Return explanation in clean readable text.
# """

# ml/explain_prompt.py
def make_explain_prompt(code, trace, concise: bool = False):
    """
    Build a clear, structured explanation prompt.
    - 'concise' will ask for a shorter explanation suitable for UI summaries.
    """
    length_hint = "short and concise" if concise else "detailed and step-by-step"
    return f"""
SYSTEM: You are an expert AI debugger and DSA instructor. Speak clearly and precisely.

USER: Explain the following code with very clear reasoning. Follow the tasks strictly and format the response as plain text.

--- Code:
{code}

--- Runtime Trace / Metadata:
{trace}

--- Tasks (strict order):
1) Short summary (one or two sentences).
2) Line-by-line explanation (explain each meaningful line or block).
3) Use the trace to illustrate how key variables change (show examples from the trace).
4) Point out potential bugs, edge-cases, and failure modes.
5) Provide concise suggestions to improve correctness, complexity, or readability.

Instructions:
- Make the explanation {length_hint}.
- Use numbered lists and short paragraphs.
- If you reference a specific trace event, include the event index or a short snippet so the frontend can highlight it.
- Do NOT include code fixes here (those come from the fix endpoint).
- Return plain readable text (no JSON) unless explicitly asked.

END
"""

