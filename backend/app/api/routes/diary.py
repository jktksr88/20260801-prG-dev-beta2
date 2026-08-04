from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import owned_plan_or_404
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.diary.crop_recognition import resolve_crop_reference
from app.diary.service import (
    build_diary_response,
    build_multi_diary_response,
    clarification_guidance,
    observation_for_crop,
    sanitize_text,
)
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
    return str(
        crop.get("name_id")
        if language == "id"
        else crop.get("name_en") or crop.get("name_id") or crop.get("slug")
    )


def _crop_contexts(recognition: dict, combined: str, language: str) -> list[dict]:
    match_by_slug = {
        item.get("crop", {}).get("slug"): item
        for item in recognition.get("matches", [])
        if isinstance(item, dict)
    }
    contexts: list[dict] = []
    for crop in recognition.get("crops", []):
        match = match_by_slug.get(crop.get("slug"), {})
        contexts.append(
            {
                "crop_name": _crop_label(crop, language),
                "crop": crop,
                "matched_alias": match.get("matched_alias"),
                "confidence": match.get("confidence", recognition.get("confidence", 0.0)),
                "method": match.get("method", recognition.get("method", "unresolved")),
                "observation": observation_for_crop(combined, crop, match.get("matched_alias")),
            }
        )
    return contexts


def _detected_crop_payloads(recognition: dict, language: str) -> list[dict]:
    contexts = _crop_contexts(recognition, "", language)
    return [
        {
            "slug": item["crop"].get("slug"),
            "name": item["crop_name"],
            "confidence": float(item.get("confidence") or 0.0),
            "method": str(item.get("method") or "unresolved"),
        }
        for item in contexts
        if item.get("crop", {}).get("slug") and item.get("crop_name")
    ]


@router.post("/guest-advice", response_model=GuestDiaryAdviceResponse)
async def guest_advice(payload: GuestDiaryAdviceRequest, request: Request):
    """Return contextual advice without creating an account or server record.

    Crop context is resolved from the user's free-form note. One note may refer
    to several crops; each verified crop remains separate in the response.
    """
    limit_ai(request)
    entry_text = sanitize_text(payload.entry_text) or ""
    question = sanitize_text(payload.user_question)
    combined = " ".join(filter(None, [entry_text, question]))
    recognition = await resolve_crop_reference(_plan_crops(payload.plan_data), combined, payload.language)
    detected_crops = recognition.get("crops", [])
    common_context = {
        "plan": payload.plan_data,
        "planner_input": payload.planner_input,
        "growth_stage": sanitize_text(payload.growth_stage),
        "weather": payload.plan_data.get("environment", {}) if isinstance(payload.plan_data, dict) else {},
        "previous_entries": payload.previous_entries[-6:],
    }

    if len(detected_crops) == 1:
        crop = detected_crops[0]
        context = {
            **common_context,
            "crop_name": _crop_label(crop, payload.language),
            "crop": crop,
        }
        guidance = await build_diary_response(context, question, entry_text, payload.language)
    elif len(detected_crops) > 1:
        contexts = _crop_contexts(recognition, combined, payload.language)
        guidance = await build_multi_diary_response(
            contexts,
            common_context,
            question,
            entry_text,
            payload.language,
        )
    else:
        guidance = clarification_guidance(combined, payload.language, recognition.get("options", []))

    singular = detected_crops[0] if len(detected_crops) == 1 else None
    detected_payloads = _detected_crop_payloads(recognition, payload.language)
    return {
        "ai_response": guidance["response"],
        "concern_level": guidance["concern_level"],
        "detected_topics": guidance["topics"],
        "recommended_next_action": guidance["next_action"],
        "follow_up_date": guidance["follow_up_date"],
        "provider_status": guidance.get("provider_status", "deterministic_fallback"),
        "detected_crop_slug": singular.get("slug") if singular else None,
        "detected_crop_name": _crop_label(singular, payload.language),
        "crop_detection_confidence": recognition.get("confidence", 0.0),
        "crop_detection_method": recognition.get("method", "unresolved"),
        "clarification_needed": recognition.get("clarification_needed", False),
        "clarification_options": recognition.get("options", []),
        "detected_crops": detected_payloads,
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

    plan_crops = _plan_crops(plan.plan_data)
    recognition: dict
    linked_crop: CropProfile | None = None

    if payload.crop_profile_id:
        linked_crop = db.get(CropProfile, payload.crop_profile_id)
        if not linked_crop:
            raise HTTPException(404, "Crop profile not found")
        detected = next((item for item in plan_crops if item.get("slug") == linked_crop.slug), None)
        recognition = {
            "crop": detected,
            "crops": [detected] if detected else [],
            "matches": [],
            "confidence": 1.0,
            "method": "explicit_crop_profile",
            "clarification_needed": False,
            "options": [],
        }
    else:
        recognition = await resolve_crop_reference(plan_crops, combined, payload.language)
        detected_crops = recognition.get("crops", [])
        if len(detected_crops) == 1:
            detected = detected_crops[0]
            detected_id = detected.get("id")
            if detected_id:
                linked_crop = db.get(CropProfile, detected_id)
            if not linked_crop and detected.get("slug"):
                linked_crop = db.scalar(select(CropProfile).where(CropProfile.slug == detected["slug"]))

    detected_crops = recognition.get("crops", [])
    common_context = {
        "plan": plan.plan_data,
        "planner_input": plan.planner_input,
        "growth_stage": sanitize_text(payload.growth_stage),
        "weather": plan.plan_data.get("environment", {}) if isinstance(plan.plan_data, dict) else {},
    }
    if len(detected_crops) == 1:
        detected = detected_crops[0]
        context = {
            **common_context,
            "crop_name": _crop_label(detected, payload.language),
            "crop": detected,
        }
        guidance = await build_diary_response(context, question, entry_text, payload.language)
    elif len(detected_crops) > 1:
        guidance = await build_multi_diary_response(
            _crop_contexts(recognition, combined, payload.language),
            common_context,
            question,
            entry_text,
            payload.language,
        )
    else:
        labels = [_crop_label(item, payload.language) for item in plan_crops]
        guidance = clarification_guidance(combined, payload.language, [label for label in labels if label])

    entry = DiaryEntry(
        user_id=user.id,
        plan_id=plan.id,
        crop_profile_id=linked_crop.id if linked_crop else None,
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
