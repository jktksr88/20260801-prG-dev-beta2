from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import owned_plan_or_404
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.diary.crop_recognition import resolve_crop_reference
from app.diary.service import build_diary_response, clarification_guidance, sanitize_text
from app.models import CropProfile, DiaryEntry, User
from app.schemas.diary import (
    DiaryCreate,
    DiaryResponse,
    GuestDiaryAdviceRequest,
    GuestDiaryAdviceResponse,
)
from app.services.rate_limit import limit_ai

router = APIRouter(prefix="/diary", tags=["diary"])


def _plan_crops(plan_data: dict) -> list[dict]:
    crops = plan_data.get("crops", []) if isinstance(plan_data, dict) else []
    return [crop for crop in crops if isinstance(crop, dict) and crop.get("slug")]


def _crop_label(crop: dict | None, language: str) -> str | None:
    if not crop:
        return None
    return str(crop.get("name_id") if language == "id" else crop.get("name_en") or crop.get("name_id") or crop.get("slug"))


@router.post("/guest-advice", response_model=GuestDiaryAdviceResponse)
async def guest_advice(payload: GuestDiaryAdviceRequest, request: Request):
    """Return contextual advice without creating an account or server record.

    Crop context is resolved from the user's free-form note. The optional
    payload.crop field is retained for backward compatibility but is not used
    as a silent default, preventing the previously opened crop from leaking
    into an unrelated diary response.
    """
    limit_ai(request)
    entry_text = sanitize_text(payload.entry_text) or ""
    question = sanitize_text(payload.user_question)
    combined = " ".join(filter(None, [entry_text, question]))
    crops = _plan_crops(payload.plan_data)
    recognition = await resolve_crop_reference(crops, combined, payload.language)
    crop = recognition.get("crop")

    if crop:
        context = {
            "plan": payload.plan_data,
            "planner_input": payload.planner_input,
            "crop_name": _crop_label(crop, payload.language),
            "crop": crop,
            "growth_stage": sanitize_text(payload.growth_stage),
            "weather": payload.plan_data.get("environment", {}) if isinstance(payload.plan_data, dict) else {},
            "previous_entries": payload.previous_entries[-6:],
        }
        guidance = await build_diary_response(context, question, entry_text, payload.language)
    else:
        guidance = clarification_guidance(combined, payload.language, recognition.get("options", []))

    return {
        "ai_response": guidance["response"],
        "concern_level": guidance["concern_level"],
        "detected_topics": guidance["topics"],
        "recommended_next_action": guidance["next_action"],
        "follow_up_date": guidance["follow_up_date"],
        "provider_status": guidance.get("provider_status", "deterministic_fallback"),
        "detected_crop_slug": crop.get("slug") if crop else None,
        "detected_crop_name": _crop_label(crop, payload.language),
        "crop_detection_confidence": recognition.get("confidence", 0.0),
        "crop_detection_method": recognition.get("method", "unresolved"),
        "clarification_needed": recognition.get("clarification_needed", False),
        "clarification_options": recognition.get("options", []),
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
    entry_text = sanitize_text(payload.entry_text) or ""
    question = sanitize_text(payload.user_question)
    combined = " ".join(filter(None, [entry_text, question]))

    crop = None
    if payload.crop_profile_id:
        crop = db.get(CropProfile, payload.crop_profile_id)
        if not crop:
            raise HTTPException(404, "Crop profile not found")
    else:
        recognition = await resolve_crop_reference(_plan_crops(plan.plan_data), combined, payload.language)
        detected = recognition.get("crop")
        detected_id = detected.get("id") if detected else None
        if detected_id:
            crop = db.get(CropProfile, detected_id)
        if not crop and detected and detected.get("slug"):
            crop = db.scalar(select(CropProfile).where(CropProfile.slug == detected["slug"]))

    if crop:
        context = {
            "plan": plan.plan_data,
            "planner_input": plan.planner_input,
            "crop_name": crop.name_id if payload.language == "id" else crop.name_en,
            "crop": next((c for c in _plan_crops(plan.plan_data) if c.get("slug") == crop.slug), {}),
            "weather": plan.plan_data.get("environment", {}) if isinstance(plan.plan_data, dict) else {},
        }
        guidance = await build_diary_response(context, question, entry_text, payload.language)
    else:
        labels = [_crop_label(item, payload.language) for item in _plan_crops(plan.plan_data)]
        guidance = clarification_guidance(combined, payload.language, [label for label in labels if label])

    entry = DiaryEntry(
        user_id=user.id,
        plan_id=plan.id,
        crop_profile_id=crop.id if crop else None,
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
