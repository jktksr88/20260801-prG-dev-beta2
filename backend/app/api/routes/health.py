from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings

router=APIRouter(tags=["health"])
@router.get("/health")
def health(): return {"status":"ok","service":"groe","build":settings.build_version}

@router.get("/build")
def build(): return {"service":"groe","build":settings.build_version}
@router.get("/ready")
def ready(db:Session=Depends(get_db)):
    try: db.execute(text("SELECT 1")); return {"status":"ready","build":settings.build_version}
    except Exception: raise HTTPException(503,"Database unavailable")
