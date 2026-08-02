from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.session import get_db

router=APIRouter(tags=["health"])
@router.get("/health")
def health(): return {"status":"ok","service":"groe"}
@router.get("/ready")
def ready(db:Session=Depends(get_db)):
    try: db.execute(text("SELECT 1")); return {"status":"ready"}
    except Exception: raise HTTPException(503,"Database unavailable")
