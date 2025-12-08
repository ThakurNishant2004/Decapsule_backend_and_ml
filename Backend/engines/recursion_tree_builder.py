# backend/engines/recursion_tree_builder.py
from typing import List, Dict, Any


def build_recursion_tree(events: List[Dict[str, Any]]) -> Dict:
    """
    Convert linear call/return events into a nested tree structure.
    """
    stack = []
    root = None

    for ev in events:
        if ev["event"] == "call":
            node = {
                "func": ev.get("func_name"),
                "args": ev.get("locals", {}),
                "children": [],
                "return": None
            }
            if stack:
                # add as child of last element
                stack[-1]["children"].append(node)
            else:
                # this is the root
                root = node
            stack.append(node)

        elif ev["event"] == "return":
            if stack:
                stack[-1]["return"] = ev.get("return_value")
                stack.pop()

    return root
