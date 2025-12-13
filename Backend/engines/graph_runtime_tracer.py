# engines/graph_runtime_tracer.py
from collections import deque

def trace_graph_runtime(code: str):
    events = []

    runtime_env = {
        "__builtins__": __builtins__,
        "deque": deque
    }

    try:
        # 1️⃣ Execute user code safely
        exec(code, runtime_env, runtime_env)

        # 2️⃣ Validate graph
        if "graph" not in runtime_env:
            return [{
                "type": "graph_error",
                "error": "Variable 'graph' not found"
            }]

        graph = runtime_env["graph"]

        if not isinstance(graph, dict) or not graph:
            return [{
                "type": "graph_error",
                "error": "Graph is empty or invalid"
            }]

        # 3️⃣ ABSOLUTE FIX: choose deterministic start node
        # This NEVER fails
        start = next(iter(graph.keys()))

        visited = set()
        q = deque([start])
        visited.add(start)

        events.append({
            "type": "init",
            "start": start,
            "queue": list(q),
            "visited": list(visited)
        })

        # 4️⃣ BFS with LIVE GRAPH MAP EVENTS
        while q:
            node = q.popleft()

            events.append({
                "type": "visit",
                "node": node,
                "queue": list(q),
                "visited": list(visited)
            })

            for nei in graph.get(node, []):
                if nei not in visited:
                    visited.add(nei)
                    q.append(nei)

                    events.append({
                        "type": "edge",
                        "from": node,
                        "to": nei,
                        "queue": list(q),
                        "visited": list(visited)
                    })

    except Exception as e:
        return [{
            "type": "graph_error",
            "error": str(e)
        }]

    return events
