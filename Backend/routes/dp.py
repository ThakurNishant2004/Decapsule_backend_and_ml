from fastapi import APIRouter
from pydantic import BaseModel
from engines.dp_engine import analyze_dp

router = APIRouter()

class DPRequest(BaseModel):
    code: str

@router.post("/")
async def dp_route(req: DPRequest):
    result = analyze_dp(req.code)
    return {
        "ok": True,
        "dp_analysis": result
    }
