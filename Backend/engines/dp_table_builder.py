def trace_dp_bottomup(code: str, max_steps: int = 200):
    steps = []

    runtime_env = {
        "__builtins__": {
            "range": range,
            "len": len,
            "list": list,
            "min": min,
            "max": max,
        }
    }

    try:
        exec(code, runtime_env, runtime_env)

        # Find dp table
        dp = runtime_env.get("dp")
        if dp is None:
            return [{
                "type": "dp_error",
                "error": "dp table not found"
            }]

        # Snapshot final dp
        steps.append({
            "type": "dp_final",
            "table": dp
        })

    except Exception as e:
        return [{
            "type": "dp_error",
            "error": str(e)
        }]

    return steps
