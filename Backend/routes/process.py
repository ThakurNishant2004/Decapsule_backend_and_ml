from fastapi import APIRouter
from pydantic import BaseModel

# Engines
from engines.classifier import classify_code
from engines.recursion_engine import trace_recursion_runtime
from engines.recursion_tree_builder import build_recursion_tree
from engines.dp_engine import analyze_dp, simulate_lis_dp
from engines.debugger import debug_code_static
from engines.array_engine import analyze_array_code
from engines.string_engine import analyze_string_code

# Sandbox
from sandbox.sandbox_runner import run_in_sandbox

# LLM
from ml.gemini_client import call_gemini
from ml.explain_prompt import make_explain_prompt


router = APIRouter()


class ProcessRequest(BaseModel):
    code: str
    input: str = ""


@router.post("/")
async def process(req: ProcessRequest):

    code = req.code
    user_input = req.input

    final = {
        "topic": None,
        "classification": None,
        "runtime": {},
        "analysis": {},
        "issues": [],
        "recursion_tree": None,
        "dp": {},
        "fix": None,
        "explanation": None
    }

    # ----------------------------------------------------
    # 1) CLASSIFIER
    # ----------------------------------------------------
    classification = classify_code(code)
    topic = classification.get("topic", "unknown")

    final["topic"] = topic
    final["classification"] = classification

    # ----------------------------------------------------
    # 2) ARRAY / STRING EXECUTION + ANALYSIS
    # ----------------------------------------------------
    if topic in ["array", "pointer"]:
        final["runtime"] = run_in_sandbox(code, user_input)
        final["analysis"] = analyze_array_code(code)

    if topic == "string":
        final["runtime"] = run_in_sandbox(code, user_input)
        final["analysis"] = analyze_string_code(code)

    # ----------------------------------------------------
    # 3) RECURSION SIMULATION
    # ----------------------------------------------------
    if topic == "recursion":
        # A better entry function guess
        entry_func = None
        for line in code.splitlines():
            if line.strip().startswith("def "):
                entry_func = line.split("(")[0].replace("def", "").strip()
                break

        trace = trace_recursion_runtime(code, entry_func, [4])

        if "data" in trace:
            events = trace["data"]["events"]
            final["recursion_tree"] = build_recursion_tree(events)

    # ----------------------------------------------------
    # 4) DP DETECTION + DP SIMULATION
    # ----------------------------------------------------
    if topic == "dp":

        dp_info = analyze_dp(code)
        final["dp"]["analysis"] = dp_info

        # If DP is LIS → simulate DP table
        if "lis" in code.lower():
            # Extract array safely using AST-free exec
            arr = []
            try:
                local_vars = {}
                exec(code, {}, local_vars)
                arr = local_vars.get("arr", [])
            except:
                arr = []

            if isinstance(arr, list):
                final["dp"]["simulation"] = simulate_lis_dp(arr)

    # ----------------------------------------------------
    # 5) STATIC BUG FINDER
    # ----------------------------------------------------
    final["issues"] = debug_code_static(code).get("issues", [])

    # ----------------------------------------------------
    # 6) AUTO-FIX PATCH
    # ----------------------------------------------------
    fix_prompt = f"""
Fix this code without changing its logic unless necessary:

{code}
"""
    final["fix"] = call_gemini(fix_prompt)

    # ----------------------------------------------------
    # 7) TEACHER EXPLANATION (Gemini)
    # ----------------------------------------------------
    explain_prompt = make_explain_prompt(code, final)
    final["explanation"] = call_gemini(explain_prompt)

    return {
        "ok": True,
        "result": final
    }
