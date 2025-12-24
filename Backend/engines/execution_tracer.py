import sys
import traceback


def safe_value(v):
    """Convert any Python value to JSON-safe."""
    try:
        if isinstance(v, (int, float, str, bool)) or v is None:
            return v
        if isinstance(v, list):
            return [safe_value(x) for x in v]
        if isinstance(v, dict):
            return {str(k): safe_value(v[k]) for k in v}
        return str(v)
    except Exception:
        return str(v)


def diff_locals(prev, curr):
    """Return only variables that changed or appeared."""
    changed = {}
    for k, v in curr.items():
        if k not in prev or prev[k] != v:
            changed[k] = v
    return changed


def trace_execution(code: str):
    events = []

    frame_history = {}

    def tracer(frame, event, arg):
        last_locals = frame_history.get(id(frame), {})

        if event == "line":
            raw_locals = {
                name: safe_value(value)
                for name, value in frame.f_locals.items()
                if name != "__builtins__"
            }

            changed = diff_locals(last_locals, raw_locals)

            events.append({
                "line_no": frame.f_lineno,
                "locals_changed": changed,
                "locals_all": raw_locals
            })

            frame_history[id(frame)] = raw_locals
        return tracer

    try:
        compiled = compile(code, "<user_code>", "exec")
        sys.settrace(tracer)
        exec(compiled, {})
        sys.settrace(None)

        return {"ok": True, "events": events}

    except Exception as e:
        sys.settrace(None)
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
