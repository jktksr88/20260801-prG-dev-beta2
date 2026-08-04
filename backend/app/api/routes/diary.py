from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import owned_plan_or_404
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.diary.service import build_diary_response, sanitize_text
from app.models import CropProfile, DiaryEntry, User
from app.schemas.diary import (
    DiaryCreate,
    DiaryResponse,
    GuestDiaryAdviceRequest,
    GuestDiaryAdviceResponse,
)
from app.services.rate_limit import limit_ai

router = APIRouter(prefix="/diary", tags=["diary"])


@router.post("/guest-advice", response_model=GuestDiaryAdviceResponse)
async def guest_advice(payload: GuestDiaryAdviceRequest, request: Request):
    """Return contextual advice without creating an account or server record."""
    limit_ai(request)
    entry_text = sanitize_text(payload.entry_text) or ""
    question = sanitize_text(payload.user_question)
    crop = payload.crop or {}
    context = {
        "plan": payload.plan_data,
        "planner_input": payload.planner_input,
        "crop_name": crop.get("name_id") if payload.language == "id" else crop.get("name_en"),
        "crop": crop,
        "growth_stage": sanitize_text(payload.growth_stage),
        "weather": payload.plan_data.get("environment", {}) if isinstance(payload.plan_data, dict) else {},
        "previous_entries": payload.previous_entries[-6:],
    }
    guidance = await build_diary_response(context, question, entry_text, payload.language)
    return {
        "ai_response": guidance["response"],
        "concern_level": guidance["concern_level"],
        "detected_topics": guidance["topics"],
        "recommended_next_action": guidance["next_action"],
        "follow_up_date": guidance["follow_up_date"],
        "provider_status": guidance.get("provider_status", "deterministic_fallback"),
    }


@router.post("", response_model=DiaryResponse, status_code=201)
async def create_entry(
    payload: DiaryCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit_ai(request)
    plan = owned_plan_or_404(db, payload.plan_id, user)
    crop = None
    if payload.crop_profile_id:
        crop = db.get(CropProfile, payload.crop_profile_id)
        if not crop:
            raise HTTPException(404, "Crop profile not found")
    entry_text = sanitize_text(payload.entry_text) or ""
    question = sanitize_text(payload.user_question)
    context = {
        "plan": plan.plan_data,
        "planner_input": plan.planner_input,
        "crop_name": (crop.name_id if payload.language == "id" else crop.name_en) if crop else None,
        "weather": plan.plan_data.get("environment", {}) if isinstance(plan.plan_data, dict) else {},
    }
    guidance = await build_diary_response(context, question, entry_text, payload.language)
    entry = DiaryEntry(
        user_id=user.id,
        plan_id=plan.id,
        crop_profile_id=payload.crop_profile_id,
        map_zone=sanitize_text(payload.map_zone),
        growth_stage=sanitize_text(payload.growth_stage),
        entry_text=entry_text,
        user_question=question,
        ai_response=guidance["response"],
        concern_level=guidance["concern_level"],
        detected_topics=guidance["topics"],
        recommended_next_action=guidance["next_action"],
        follow_up_date=guidance["follow_up_date"],
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[DiaryResponse])
def list_entries(plan_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned_plan_or_404(db, plan_id, user)
    return db.scalars(
        select(DiaryEntry)
        .where(DiaryEntry.plan_id == plan_id, DiaryEntry.user_id == user.id)
        .order_by(DiaryEntry.entry_date.desc())
    ).all()


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.get(DiaryEntry, entry_id)
    if not entry or entry.user_id != user.id:
        raise HTTPException(404, "Diary entry not found")
    db.delete(entry)
    db.commit()
