# backend/routes/fix.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def placeholder_fix():
    return {"status": "ok", "message": "fix route placeholder"}
