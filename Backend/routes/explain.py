from fastapi import APIRouter
from pydantic import BaseModel
# from ml.gemini_client import call_gemini
from ml.groq_client import call_groq as call_llm
from ml.explain_prompt import make_explain_prompt

router = APIRouter()

class ExplainRequest(BaseModel):
    code: str
    trace: dict

@router.post("/")
async def explain(req: ExplainRequest):

    prompt = make_explain_prompt(req.code, req.trace)

    result = call_llm(prompt)

    return {
        "ok": True,
        "explanation": result
    }
