# import sys

# def trace_dp_runtime(code: str, entry_func: str, args: list):
#     events = []
#     seen_states = set()

#     def tracer(frame, event, arg):
#         if event == "line":
#             for name, val in frame.f_locals.items():
#                 if (
#                     isinstance(val, dict)
#                     and val
#                     and name.lower() in ("memo", "dp", "cache")
#                 ):
#                     state = (name, tuple(sorted(val.items())))
#                     if state not in seen_states:
#                         seen_states.add(state)
#                         events.append({
#                             "type": "dp_update",
#                             "memo_name": name,
#                             "table": dict(sorted(val.items()))
#                         })
#         return tracer

#     exec_env = {}

#     sys.settrace(tracer)
#     try:
#         # remove print calls
#         clean_lines = []
#         for line in code.splitlines():
#             if entry_func and line.strip().startswith("print") and f"{entry_func}(" in line:
#                 continue
#             clean_lines.append(line)

#         clean_code = "\n".join(clean_lines)

#         exec(clean_code, exec_env, exec_env)

#         if entry_func in exec_env:
#             exec_env[entry_func](*args)

#     except Exception as e:
#         events.append({
#             "type": "dp_error",
#             "error": str(e)
#         })
#     finally:
#         sys.settrace(None)

#     return events

# engines/dp_runtime_tracer.py
# engines/dp_runtime_tracer.py
import sys
import copy

def trace_dp_runtime(code: str, entry_func: str, args: list):
    events = []
    last_snapshot = None

    def tracer(frame, event, arg):
        nonlocal last_snapshot

        if event == "line":
            for name, val in frame.f_locals.items():
                # STRICT FILTER
                if (
                    isinstance(val, dict)
                    and val
                    and all(isinstance(k, (int, str)) and isinstance(v, (int, float)) for k, v in val.items())
                ):
                    snapshot = dict(sorted(val.items()))
                    if snapshot != last_snapshot:
                        last_snapshot = copy.deepcopy(snapshot)
                        events.append({
                            "type": "dp_update",
                            "memo_name": str(name),
                            "table": snapshot
                        })
        return tracer

    runtime_env = {}

    sys.settrace(tracer)
    try:
        # CRITICAL: shared globals/locals
        exec(code, runtime_env, runtime_env)

        if entry_func not in runtime_env:
            events.append({
                "type": "dp_error",
                "error": f"Entry function '{entry_func}' not found"
            })
            return events

        runtime_env[entry_func](*args)

    except Exception as e:
        events.append({
            "type": "dp_error",
            "error": str(e)
        })
    finally:
        sys.settrace(None)

    return events
