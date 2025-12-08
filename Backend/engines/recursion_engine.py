# backend/engines/recursion_engine.py
import json
import uuid
import os
import subprocess
import textwrap
from typing import Any, Dict, List, Optional

TMP_DIR = "/tmp" if os.name != "nt" else os.getenv("TEMP", "C:\\Temp")


def _make_tracer_script(user_code: str, entry_func: str, entry_args: List[Any]) -> str:
    """
    Build a python script that:
      - defines a tracer via sys.settrace
      - executes user's code
      - calls entry_func(*entry_args)
      - prints JSON trace to stdout
    """
    # safe-ish JSON encoding of args for literal insertion
    args_repr = ", ".join(repr(a) for a in entry_args)

    tracer_py = f"""
import sys, json, traceback

trace_events = []

def safe_snapshot(frame):
    # capture selected locals (stringified) to avoid unserializable objects
    try:
        locs = {{
            k: repr(v) for k, v in frame.f_locals.items()
            if not k.startswith("__")
        }}
    except Exception as e:
        locs = {{}}
    return locs

def tracer(frame, event, arg):
    # only handle function calls and returns
    if event == 'call':
        code = frame.f_code
        trace_events.append({{
            "event": "call",
            "func_name": code.co_name,
            "filename": code.co_filename,
            "lineno": frame.f_lineno,
            "locals": safe_snapshot(frame)
        }})
    elif event == 'return':
        try:
            ret = repr(arg)
        except Exception:
            ret = "<unreprable>"
        trace_events.append({{
            "event": "return",
            "func_name": frame.f_code.co_name,
            "filename": frame.f_code.co_filename,
            "lineno": frame.f_lineno,
            "return_value": ret,
            "locals": safe_snapshot(frame)
        }})
    return tracer

# USER CODE START
{user_code}
# USER CODE END

def _run_and_trace():
    sys.settrace(tracer)
    try:
        result = {entry_func}({args_repr})
    except Exception as e:
        # capture exception stack for debugging
        tb = traceback.format_exc()
        sys.settrace(None)
        print(json.dumps({{"error": "runtime exception", "traceback": tb, "events": trace_events}}))
        return
    sys.settrace(None)
    # final output
    print(json.dumps({{"result_repr": repr(result), "events": trace_events}}))

if __name__ == '__main__':
    _run_and_trace()
"""
    # Dedent for neatness and return
    return textwrap.dedent(tracer_py)


def trace_recursion_runtime(code: str, entry_func: str, entry_args: Optional[List[Any]] = None, timeout: int = 3) -> Dict:
    """
    Executes the user's code inside a traced temporary script and returns the JSON trace.
    - code: full python code string (must include entry_func)
    - entry_func: the function name to call (string)
    - entry_args: list of python-serializable arguments (e.g., [4] for fact(4))
    - timeout: subprocess timeout in seconds
    """
    if entry_args is None:
        entry_args = []

    file_id = str(uuid.uuid4()).replace("-", "")[:16]
    tmp_file = os.path.join(TMP_DIR, f"decap_trace_{file_id}.py")

    script = _make_tracer_script(code, entry_func, entry_args)

    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(script)

    try:
        proc = subprocess.run(
            ["python", tmp_file],
            capture_output=True,
            timeout=timeout,
            check=False,
            text=True
        )
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        if stderr:
            # include stderr in response to aid debugging
            return {"error": "stderr", "stderr": stderr, "stdout": stdout}
        if not stdout:
            return {"error": "no output", "stdout": stdout}
        try:
            parsed = json.loads(stdout)
            return {"ok": True, "data": parsed}
        except Exception as e:
            return {"error": f"json-parse-failed: {e}", "raw_stdout": stdout}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "message": "Execution timed out (possible infinite recursion)"}
    except Exception as e:
        return {"error": "execution_failed", "message": str(e)}
    finally:
        # try to remove temp file
        try:
            os.remove(tmp_file)
        except Exception:
            pass
