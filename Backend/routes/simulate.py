from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict


from engines.recursion_engine import trace_recursion_runtime
from engines.recursion_tree_builder import build_recursion_tree
from engines.dp_engine import simulate_lis_dp


router = APIRouter()


class SimRequest(BaseModel):
    code: str
    topic: str = "recursion"
    entry_func: str = None
    entry_args: list = []


@router.post("/")
async def simulate(req: SimRequest) -> Dict[str, Any]:
    # CURRENTLY ONLY SUPPORT RECURSION
    if req.topic == "recursion":
        if not req.entry_func:
            return {"error": "entry_func required for recursion simulation"}

        raw = trace_recursion_runtime(
            req.code,
            req.entry_func,
            req.entry_args
        )

        # If something went wrong in the sandbox runner
        if "data" not in raw:
            return raw
        if "events" not in raw["data"]:
            return raw

        events = raw["data"]["events"]
        tree = build_recursion_tree(events)

        return {
            "ok": True,
            "result": raw["data"].get("result_repr"),
            "events": events,
            "tree": tree,
        }
    
        # DP - LIS simulation
    if req.topic == "dp_lis":
        # For dp, we expect `code` to be a JSON-style array string like "[3,1,5,2,6]"
        try:
            # safely evaluate simple list formats. Accept JSON array string or python list syntax.
            import json
            arr = json.loads(req.code)
            if not isinstance(arr, list):
                return {"error": "For dp_lis, code must be a JSON array like \"[3,1,5]\""}
        except Exception:
            # fallback: try python eval but in controlled way
            try:
                arr = eval(req.code, {"__builtins__": {}}, {})
                if not isinstance(arr, list):
                    return {"error": "For dp_lis, code must evaluate to a list of integers"}
            except Exception as e:
                return {"error": "Failed to parse array for dp_lis", "detail": str(e)}

        # validate contents are numbers
        try:
            arr = [int(x) for x in arr]
        except Exception:
            return {"error": "Array must contain integers only"}

        out = simulate_lis_dp(arr)
        return {
            "ok": True,
            "array": arr,
            "final_dp": out["final_dp"],
            "snapshots": out["snapshots"]
        }

    return {"error": "topic not supported yet"}
