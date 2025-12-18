
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
from engines.dp_runtime_tracer import trace_dp_runtime
from engines.graph_runtime_tracer import trace_graph_runtime
from engines.graph_dfs_runtime_tracer import trace_dfs_runtime
from engines.dp_bottomup_runtime_tracer import trace_dp_bottomup_runtime

# Sandbox
from sandbox.sandbox_runner import run_in_sandbox

# LLM (existing synchronous call)
# from ml.gemini_client import call_gemini
from ml.groq_client import call_groq as call_llm
from ml.explain_prompt import make_explain_prompt

router = APIRouter()


class StreamRequest(BaseModel):
    code: str
    input: str = ""


# def sse_event(data: dict, event: str = "message") -> str:
#     """
#     Simple helper to format SSE text/event-stream event
#     Each event data is JSON-stringified.
#     """
#     payload = json.dumps(data, ensure_ascii=False)
#     return f"event: {event}\ndata: {payload}\n\n"

def sse_event(data: dict, event: str = "message") -> str:
    try:
        payload = json.dumps(data, ensure_ascii=False)
    except TypeError:
        payload = json.dumps({"error": "Non-serializable payload blocked"})
    return f"event: {event}\ndata: {payload}\n\n"

def extract_top_level_call_args(code: str, func_name: str):
    """
    Extract args ONLY from top-level calls like:
    fib(10)
    bfs(graph, 1)

    Ignore:
    - def fib(...)
    - return fib(...)
    - fib(...) inside other expressions
    """
    for line in code.splitlines():
        raw = line
        line = line.strip()

        # must start at column 0 (top-level)
        if raw.startswith(" ") or raw.startswith("\t"):
            continue

        if line.startswith("def "):
            continue

        if line.startswith("#"):
            continue

        if line.startswith(f"{func_name}(") and line.endswith(")"):
            inside = line[len(func_name) + 1 : -1]
            try:
                return [
                    int(x.strip())
                    for x in inside.split(",")
                    if x.strip().isdigit()
                ]
            except Exception:
                return []

    return []



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
            elif topic == "graph_bfs":
                yield sse_event({"stage": "graph_start", "payload": {"algo": "bfs"}})

                bfs_events = trace_graph_runtime(code)

                for step in bfs_events:
                    yield sse_event({
                        "stage": "graph_step",
                        "payload": step
                    })
            elif topic == "graph_dfs":
                yield sse_event({"stage": "graph_start", "payload": {"algo": "dfs"}})

                dfs_events = trace_dfs_runtime(code)

                for step in dfs_events:
                    yield sse_event({
                        "stage": "graph_step",
                        "payload": step
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

                # -------- Extract recursion call arguments --------

                rec_args = extract_top_level_call_args(code, entry_func)

                # fallback ONLY if user never called the function
                if not rec_args:
                    rec_args = [4]

                trace = trace_recursion_runtime(code, entry_func, rec_args)
                if "data" in trace and "events" in trace["data"]:
                    events = trace["data"]["events"]
                    recursion_tree = build_recursion_tree(events)
                    yield sse_event({"stage": "recursion", "payload": {"events": events, "tree": recursion_tree}})
                else:
                    yield sse_event({"stage": "recursion_error", "payload": trace})

            if await request.is_disconnected():
                return

            # ---------- STAGE 4: dp detection + simulation ----------
            # ---------- STAGE 4: DP LIVE SIMULATION ----------
            dp_out = {
                "steps": [],
                "final_table": None
            }

            if topic in ("dp", "dp_topdown"):
                yield sse_event({"stage": "dp_start", "payload": {"mode": "top_down"}})

                entry_func = None
                for line in code.splitlines():
                    if line.strip().startswith("def "):
                        entry_func = line.split("(")[0].replace("def", "").strip()
                        break

                # 2️⃣ Extract arguments from ORIGINAL code
                dp_args = []
                for line in code.splitlines():
                    if entry_func and f"{entry_func}(" in line:
                        inside = line.split(f"{entry_func}(")[1].split(")")[0]
                        try:
                            dp_args = [int(x.strip()) for x in inside.split(",") if x.strip().isdigit()]
                        except:
                            dp_args = []
                        break

                # 3️⃣ Absolute safety fallback
                if not dp_args:
                    dp_args = [10]

                dp_events = trace_dp_runtime(code, entry_func, dp_args)

                for step in dp_events:
                    dp_out["steps"].append(step)

                    if step["type"] == "dp_update":
                        dp_out["final_table"] = step["table"]

                    yield sse_event({
                        "stage": "dp_step",
                        "payload": step
                    })
            elif topic == "dp_bottomup":
                yield sse_event({"stage": "dp_start", "payload": {"mode": "bottom_up"}})

                dp_events = trace_dp_bottomup_runtime(code)

                for step in dp_events:
                    dp_out["steps"].append(step)
                    dp_out["final_table"] = step.get("table")

                    yield sse_event({"stage": "dp_step", "payload": step})
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
            # ---------- STAGE 7: teacher explanation (LLM) ----------
            explanation = None

            if topic != "graph_dfs":   # 👈 DFS ONLY SKIP
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
                    })
                    explanation = call_llm(explain_prompt)
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
            }

            if topic != "graph_dfs" and explanation:
                final["explanation"] = explanation

            yield sse_event({"stage": "done", "payload": final})

        except asyncio.CancelledError:
            # client disconnected
            return
        except Exception as exc:
            # generic error
            yield sse_event({"stage": "error", "payload": {"error": str(exc)}})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
