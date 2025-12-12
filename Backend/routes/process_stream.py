
# routes/process_stream.py
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Engines (existing)
from engines.classifier import classify_code
from engines.recursion_engine import trace_recursion_runtime
from engines.recursion_tree_builder import build_recursion_tree
from engines.dp_engine import analyze_dp, simulate_lis_dp
from engines.debugger import debug_code_static
from engines.array_engine import analyze_array_code
from engines.string_engine import analyze_string_code

# Sandbox
from sandbox.sandbox_runner import run_in_sandbox

# LLM (existing synchronous call)
from ml.gemini_client import call_gemini
from ml.explain_prompt import make_explain_prompt

router = APIRouter()


class StreamRequest(BaseModel):
    code: str
    input: str = ""


def sse_event(data: dict, event: str = "message") -> str:
    """
    Simple helper to format SSE text/event-stream event
    Each event data is JSON-stringified.
    """
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


async def run_stage_short_delay():
    # tiny delay so UI can subscribe reliably before first yield
    await asyncio.sleep(0.05)


@router.post("/stream")
async def process_stream(req: StreamRequest, request: Request):
    code = req.code
    user_input = req.input

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # small warm-up so client is ready
            await run_stage_short_delay()

            # ---------- STAGE 1: classification ----------
            classification = classify_code(code)
            topic = classification.get("topic", "unknown")

            yield sse_event({"stage": "classification", "payload": classification})

            # check if client disconnected
            if await request.is_disconnected():
                return

            # ---------- STAGE 2: runtime (array/string/pointer) ----------
            runtime = {}
            analysis = {}
            if topic in ["array", "pointer"]:
                yield sse_event({"stage": "runtime_start", "payload": {"why": "array/pointer detected"}})
                runtime = run_in_sandbox(code, user_input)
                analysis = analyze_array_code(code)
                yield sse_event({"stage": "runtime", "payload": runtime})
                yield sse_event({"stage": "analysis", "payload": analysis})
            elif topic == "string":
                yield sse_event({"stage": "runtime_start", "payload": {"why": "string detected"}})
                runtime = run_in_sandbox(code, user_input)
                analysis = analyze_string_code(code)
                yield sse_event({"stage": "runtime", "payload": runtime})
                yield sse_event({"stage": "analysis", "payload": analysis})
            # ---------- GRAPH ANALYSIS (optional) ----------
            elif topic == "graph":
                yield sse_event({
                "stage": "graph_detected",
                "payload": {"reason": "graph-related patterns found but no graph engine implemented"}
            })
            else:
                # for unknown topics we still tell the client
                yield sse_event({"stage": "runtime_skipped", "payload": {"reason": "topic not runtime-type"}})

            if await request.is_disconnected():
                return

            # ---------- STAGE 3: recursion simulation ----------
            recursion_tree = None
            if topic == "recursion":
                yield sse_event({"stage": "recursion_start", "payload": {}})
                # attempt to find entry function
                entry_func = None
                for line in code.splitlines():
                    if line.strip().startswith("def "):
                        entry_func = line.split("(")[0].replace("def", "").strip()
                        break

                trace = trace_recursion_runtime(code, entry_func, [4])
                if "data" in trace and "events" in trace["data"]:
                    events = trace["data"]["events"]
                    recursion_tree = build_recursion_tree(events)
                    yield sse_event({"stage": "recursion", "payload": {"events": events, "tree": recursion_tree}})
                else:
                    yield sse_event({"stage": "recursion_error", "payload": trace})

            if await request.is_disconnected():
                return

            # ---------- STAGE 4: dp detection + simulation ----------
            dp_out = {}
            if topic == "dp":
                dp_info = analyze_dp(code)
                yield sse_event({"stage": "dp_analysis", "payload": dp_info})
                # try generic simulate (LIS fallback)
                # if code has explicit arr variable, try to exec-safe extract arr
                if "lis" in code.lower():
                    arr = []
                    try:
                        local_vars = {}
                        exec(code, {}, local_vars)
                        arr = local_vars.get("arr", [])
                    except:
                        arr = []
                    if isinstance(arr, list):
                        sim = simulate_lis_dp(arr)
                        dp_out["simulation"] = sim
                        yield sse_event({"stage": "dp_simulation", "payload": sim})
            else:
                yield sse_event({"stage": "dp_skipped", "payload": {"reason": "topic not dp"}})

            if await request.is_disconnected():
                return

            # ---------- STAGE 5: static bug detection ----------
            issues = debug_code_static(code).get("issues", [])
            yield sse_event({"stage": "issues", "payload": issues})

            if await request.is_disconnected():
                return

            # # ---------- STAGE 6: attempt auto-fix (LLM) ----------
            # yield sse_event({"stage": "fix_start", "payload": {}})
            # try:
            #     fix_prompt = f"Fix this code without changing its logic unless necessary:\n\n{code}"
            #     fix_text = call_gemini(fix_prompt)
            #     yield sse_event({"stage": "fix", "payload": fix_text})
            # except Exception as e:
            #     yield sse_event({"stage": "fix_error", "payload": {"error": str(e)}})

            # if await request.is_disconnected():
            #     return

            # ---------- STAGE 7: teacher explanation (LLM) ----------
            yield sse_event({"stage": "explain_start", "payload": {}})
            try:
                explain_prompt = make_explain_prompt(code, {
                    "topic": topic,
                    "classification": classification,
                    "runtime": runtime,
                    "analysis": analysis,
                    "recursion_tree": recursion_tree,
                    "dp": dp_out,
                    "issues": issues,
                    # "fix": fix_text if 'fix_text' in locals() else None
                })
                explanation = call_gemini(explain_prompt)
                yield sse_event({"stage": "explanation", "payload": explanation})
            except Exception as e:
                yield sse_event({"stage": "explain_error", "payload": {"error": str(e)}})

            # ---------- FINAL: done ----------
            final = {
                "topic": topic,
                "classification": classification,
                "runtime": runtime,
                "analysis": analysis,
                "recursion_tree": recursion_tree,
                "dp": dp_out,
                "issues": issues,
                # "fix": fix_text if 'fix_text' in locals() else None,
                "explanation": explanation if 'explanation' in locals() else None
            }
            yield sse_event({"stage": "done", "payload": final})

        except asyncio.CancelledError:
            # client disconnected
            return
        except Exception as exc:
            # generic error
            yield sse_event({"stage": "error", "payload": {"error": str(exc)}})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
