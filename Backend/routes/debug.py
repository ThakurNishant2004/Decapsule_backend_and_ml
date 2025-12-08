from fastapi import APIRouter
from pydantic import BaseModel

from engines.array_engine import simulate_array_operations
from engines.string_engine import simulate_string_operations
from engines.debugger_rules import detect_common_array_bugs, detect_common_string_bugs
from engines.execution_tracer import trace_execution

router = APIRouter()

class DebugRequest(BaseModel):
    code: str
    array: list = None
    string: str = None


@router.post("/")
async def debug(req: DebugRequest):
    all_issues = []
    analysis = {}

    # ARRAY MODE
    if req.array is not None:
        analysis = simulate_array_operations(req.code, req.array)
        issues = detect_common_array_bugs(req.code, analysis)
        all_issues.extend(issues)

    # STRING MODE
    if req.string is not None:
        analysis = simulate_string_operations(req.code, req.string)
        issues = detect_common_string_bugs(req.code, analysis)
        all_issues.extend(issues)

    runtime_steps = trace_execution(req.code)

    return {
        "analysis": analysis,
        "issues": all_issues,
        "runtime": runtime_steps
    }

