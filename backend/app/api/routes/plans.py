from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import SavedPlan, User
from app.schemas.planner import SavePlanRequest
from app.auth.dependencies import get_current_user
from app.api.deps import owned_plan_or_404

router=APIRouter(prefix="/plans",tags=["saved plans"])

def serialize(p:SavedPlan,public:bool=False):
    data={"id":p.id,"name":p.name,"language":p.language,"plan_data":p.plan_data,"share_slug":p.share_slug,"is_public":p.is_public,"created_at":p.created_at,"updated_at":p.updated_at}
    if not public: data["planner_input"]=p.planner_input
    return data

@router.post("",status_code=201)
def save_plan(payload:SavePlanRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    plan=SavedPlan(user_id=user.id,**payload.model_dump())
    db.add(plan);db.commit();db.refresh(plan);return serialize(plan)

@router.get("")
def list_plans(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(SavedPlan).where(SavedPlan.user_id==user.id).order_by(SavedPlan.updated_at.desc())).all()
    return {"items":[serialize(x) for x in rows]}

@router.get("/{plan_id}")
def get_plan(plan_id:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return serialize(owned_plan_or_404(db,plan_id,user))

@router.patch("/{plan_id}")
def update_plan(plan_id:str,payload:dict,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    plan=owned_plan_or_404(db,plan_id,user)
    for key in ["name","is_public","plan_data"]:
        if key in payload: setattr(plan,key,payload[key])
    db.commit();db.refresh(plan);return serialize(plan)

@router.delete("/{plan_id}",status_code=204)
def delete_plan(plan_id:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    plan=owned_plan_or_404(db,plan_id,user);db.delete(plan);db.commit()

public_router=APIRouter(prefix="/public/plans",tags=["public plans"])
@public_router.get("/{share_slug}")
def shared_plan(share_slug:str,db:Session=Depends(get_db)):
    plan=db.scalar(select(SavedPlan).where(SavedPlan.share_slug==share_slug,SavedPlan.is_public.is_(True)))
    if not plan: raise HTTPException(404,"Shared plan not found")
    return serialize(plan,True)
