from fastapi import APIRouter
from pydantic import BaseModel
from ml.local_llm import call_local_llm
from ml.explain_prompt import make_explain_prompt

router = APIRouter()

class ExplainRequest(BaseModel):
    code: str
    trace: dict

@router.post("/")
async def explain(req: ExplainRequest):
    prompt = make_explain_prompt(req.code, req.trace)
    result = call_local_llm(prompt)
    return {"explanation": result}
