from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import SavedPlan, User

def owned_plan_or_404(db: Session, plan_id: str, user: User) -> SavedPlan:
    plan=db.get(SavedPlan,plan_id)
    if not plan or plan.user_id!=user.id:
        raise HTTPException(404,"Plan not found")
    return plan
