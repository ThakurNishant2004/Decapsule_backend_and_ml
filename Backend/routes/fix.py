from fastapi import APIRouter
from pydantic import BaseModel
from ml.gemini_client import call_gemini
from ml.fix_prompt import make_fix_prompt
from engines.debugger import analyze_code_for_issues

router = APIRouter()

class FixRequest(BaseModel):
    code: str

@router.post("/")
async def fix(req: FixRequest):

    # 1. Detect Issues (our own rule engine)
    issues = analyze_code_for_issues(req.code)

    # 2. Prepare prompt for LLM
    prompt = make_fix_prompt(req.code, issues)

    # 3. Ask Gemini for fixed code
    fixed = call_gemini(prompt)

    return {
        "ok": True,
        "issues": issues,
        "fixed_code": fixed
    }
