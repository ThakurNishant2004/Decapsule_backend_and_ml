from fastapi import APIRouter
from pydantic import BaseModel
from sandbox.sandbox_runner import run_in_sandbox

router = APIRouter()

class RunRequest(BaseModel):
    code: str
    input: str = ""

@router.post("/")
async def run(req: RunRequest):
    result = run_in_sandbox(req.code, req.input)
    return result
