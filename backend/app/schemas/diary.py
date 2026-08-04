from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DiaryCreate(BaseModel):
    plan_id: str
    crop_profile_id: str | None = None
    map_zone: str | None = Field(default=None, max_length=120)
    growth_stage: str | None = Field(default=None, max_length=80)
    entry_text: str = Field(min_length=1, max_length=10000)
    user_question: str | None = Field(default=None, max_length=4000)
    language: str = Field(default="en", pattern="^(en|id)$")


class GuestDiaryAdviceRequest(BaseModel):
    plan_data: dict[str, Any]
    planner_input: dict[str, Any]
    crop: dict[str, Any] | None = None
    previous_entries: list[dict[str, Any]] = Field(default_factory=list, max_length=12)
    growth_stage: str | None = Field(default=None, max_length=80)
    entry_text: str = Field(min_length=1, max_length=10000)
    user_question: str | None = Field(default=None, max_length=4000)
    language: str = Field(default="en", pattern="^(en|id)$")


class GuestDiaryAdviceResponse(BaseModel):
    ai_response: str
    concern_level: str
    detected_topics: list[str]
    recommended_next_action: str | None
    follow_up_date: datetime | None
    provider_status: str


class DiaryResponse(BaseModel):
    id: str
    plan_id: str
    crop_profile_id: str | None
    map_zone: str | None
    entry_date: datetime
    growth_stage: str | None
    entry_text: str
    user_question: str | None
    ai_response: str | None
    concern_level: str
    detected_topics: list
    recommended_next_action: str | None
    follow_up_date: datetime | None
    model_config = {"from_attributes": True}
