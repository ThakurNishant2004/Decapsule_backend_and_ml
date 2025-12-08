# backend/routes/analyze.py
from fastapi import APIRouter
from pydantic import BaseModel
from engines.classifier import classify_code
from ml.local_llm import call_local_llm

router = APIRouter()


class AnalyzeRequest(BaseModel):
    code: str
    use_ml: bool = False  # optionally call LLM fallback


@router.post("/")
async def analyze(req: AnalyzeRequest):
    code = req.code
    # first do fast heuristics
    result = classify_code(code, use_ml_fallback=req.use_ml)

    # if result asks for ML fallback, optionally call local llm
    if result.get("topic") == "ml_fallback" and req.use_ml:
        prompt = f"""You are a code classifier. Given the code below, reply JSON with fields:
{{ "topic": <one of recursion, dp, graph, array, string, pointer, unknown>, "reason": "<short reason>" }}.
Code:
{code}
"""
        llm_out = call_local_llm(prompt)
        # try to parse simple JSON from llm_out
        import json
        try:
            parsed = json.loads(llm_out)
            # validate fields
            topic = parsed.get("topic", "unknown")
            reason = parsed.get("reason", "")
            return {"topic": topic, "confidence": 0.6, "reasons": ["ML fallback: " + reason]}
        except Exception:
            # If parsing fails, return LLM raw text
            return {"topic": "unknown", "confidence": 0.4, "reasons": [f"llm: {llm_out}"]}

    return result
