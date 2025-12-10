# backend/engines/classifier.py
import ast
import re
from typing import Tuple, List, Dict


def _contains_patterns(code: str, patterns: List[str]) -> bool:
    txt = code.lower()
    return any(p.lower() in txt for p in patterns)


def _detect_recursion(code: str) -> Tuple[bool, str]:
    """
    Detect recursion by parsing functions and checking if a function calls itself.
    Returns (detected, reason).
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return False, "AST parse failed"

    func_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    for f in func_defs:
        fname = f.name
        # walk body to find Call nodes that call the same name
        for node in ast.walk(f):
            if isinstance(node, ast.Call):
                # function call might be attribute or name
                if isinstance(node.func, ast.Name) and node.func.id == fname:
                    return True, f"Function '{fname}' calls itself (recursion)"
                if isinstance(node.func, ast.Attribute) and node.func.attr == fname:
                    return True, f"Method '{fname}' appears to call itself"
    return False, "No self-call found in functions"


def _detect_dp(code: str) -> Tuple[bool, str]:
    """
    Heuristics for DP:
      - presence of variable named dp
      - nested loops often (for i in range... for j in range...)
      - memoization patterns (cache decorator, memo, dictionary storing)
    """
    if re.search(r"\bdp\b", code):
        return True, "Found dp[] usage"
    if "memo" in code or "cache" in code or "lru_cache" in code:
        return True, "Memoization keywords detected"

    # nested loop DP heuristic (safer)
    loop_pairs = re.findall(r"for .* in range", code)
    if len(loop_pairs) >= 2 and "dp" in code:
        return True, "Nested loops + dp[] suggests DP"

    return False, "No dp or memoization found"

def _detect_graph(code: str) -> Tuple[bool, str]:
    """
    Heuristics for graph code:
      - keywords: edges, adjacency, graph, bfs, dfs, dijkstra, prim, kruskal
      - typical patterns like adjacency list (list of lists) or edge list
    """
    graph_keywords = ["bfs(", "dfs(", "dijkstra", "kruskal", "prim", "adjacency", "adj", "edges", "graph"]
    if _contains_patterns(code, graph_keywords):
        return True, "Found graph-related keywords (bfs/dfs/dijkstra/adjacency/edges)"
    # adjacency list pattern: list of lists e.g., [[] for _ in range(n)]
    if re.search(r"\[\s*\]\s*for\s+_?\s+in\s+range", code):
        return True, "Adjacency-list pattern detected"
    return False, "No graph patterns"


def _detect_array_string(code: str) -> Tuple[bool, str]:
    """
    Detect array or string code.
    """

    # detect string literal indexing: s = "hello"; s[3]
    string_assignment = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(['\"].*?['\"])", code)
    indexing = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[[^\]]+\]", code)

    if string_assignment and indexing:
        var1 = string_assignment.group(1)
        var2 = indexing.group(1)
        if var1 == var2:
            return True, "String indexing detected"

    # detect general string methods
    string_kw = ["split(", "join(", "substring", "str(", ".upper(", ".lower(", "replace("]
    if any(k in code for k in string_kw):
        return True, "String manipulation keywords detected"

    # detect array variables
    if re.search(r"\b(arr|nums|array|list|vector)\b", code) and indexing:
        return True, "Indexing and array variable names detected"

    # generic indexing → default as array
    if indexing:
        return True, "Indexing detected"

    return False, "No array/string patterns found"



def _detect_pointer(code: str) -> Tuple[bool, str]:
    """
    Detect real C/C++ pointer patterns, NOT Python's '*'.
    We detect:
      - '->'
      - malloc(), free()
      - int* p; or char* s;  (but NOT python math)
    """
    # definitely C/C++
    if "->" in code or "malloc(" in code or "free(" in code:
        return True, "Found C/C++ memory-operation (->, malloc, free)"

    # detect C-style declarations ONLY if '*' is next to a type keyword
    type_keywords = ["int", "char", "float", "double", "long"]
    for t in type_keywords:
        if re.search(rf"\b{t}\s*\*", code):
            return True, f"Detected C-style pointer declaration ({t}*)"

    return False, "No pointer patterns"



def classify_code(code: str, use_ml_fallback: bool = False) -> Dict:
    """
    Return dict:
    {
      "topic": "recursion" | "dp" | "graph" | "array" | "string" | "pointer" | "unknown",
      "confidence": 0.0-1.0,
      "reasons": [...]
    }
    """
    reasons: List[str] = []
    score = {}

    rec, reason = _detect_recursion(code)
    if rec:
        reasons.append(reason)
        score["recursion"] = 1.0

    dp, reason = _detect_dp(code)
    if dp:
        reasons.append(reason)
        score["dp"] = max(score.get("dp", 0.0), 0.9)

    graph, reason = _detect_graph(code)
    if graph:
        reasons.append(reason)
        score["graph"] = max(score.get("graph", 0.0), 0.9)

    arrstr, reason = _detect_array_string(code)
    if arrstr:
        reasons.append(reason)
        score["array_string"] = max(score.get("array_string", 0.0), 0.8)

    ptr, reason = _detect_pointer(code)
    if ptr:
        reasons.append(reason)
        score["pointer"] = max(score.get("pointer", 0.0), 0.85)

    # If multiple scores, pick best
    if score:
        # pick the topic with highest score
        topic = max(score.items(), key=lambda kv: kv[1])[0]
        confidence = float(score[topic])
        # map internal 'array_string' to 'array' or 'string' based on keywords
        if topic == "array_string":
    # If string literal present anywhere, classify as string
            if "'" in code or '"' in code:
                topic = "string"
            else:
                topic = "array"
        return {"topic": topic, "confidence": confidence, "reasons": reasons}

    # fallback heuristic: small heuristics using keywords
    if _contains_patterns(code, ["sort(", ".sort(", "sorted(", "binary search", "binary_search"]):
        return {"topic": "array", "confidence": 0.7, "reasons": ["Sort / search keywords detected"]}

    # Optionally use an LLM fallback (if enabled externally)
    if use_ml_fallback:
        # return a special marker. The route will call an ML client if configured.
        return {"topic": "ml_fallback", "confidence": 0.4, "reasons": ["no strong heuristics matched - request ML fallback"]}

    return {"topic": "unknown", "confidence": 0.25, "reasons": ["no heuristics matched"]}
