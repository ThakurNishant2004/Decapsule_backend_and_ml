def trace_dfs_runtime(code: str, max_events: int = 200):
    events = []

    runtime_env = {
        "__builtins__": {
            "set": set, "list": list, "dict": dict,
            "len": len, "range": range, "print": print,
        }
    }

    exec(code, runtime_env, runtime_env)

    graph = runtime_env.get("graph")
    if not isinstance(graph, dict) or not graph:
        return [{"type": "graph_error", "error": "Invalid graph"}]

    runtime_env.pop("dfs", None)  # 🔥 KEY FIX

    visited = set()
    call_stack = []
    start = next(iter(graph))

    def _trace_dfs(node):
        if len(events) >= max_events:
            return
        visited.add(node)
        call_stack.append(node)

        events.append({"type": "dfs_call", "node": node, "depth": len(call_stack)})

        for nei in graph.get(node, []):
            events.append({"type": "dfs_edge", "from": node, "to": nei})
            if nei not in visited:
                _trace_dfs(nei)

        call_stack.pop()
        events.append({"type": "dfs_return", "node": node, "depth": len(call_stack)})

    _trace_dfs(start)
    return events
