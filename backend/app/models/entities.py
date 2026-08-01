from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


def uuid_str() -> str:
    return str(uuid4())

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    plans: Mapped[list["SavedPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    diary_entries: Mapped[list["DiaryEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped[User] = relationship(back_populates="refresh_tokens")

class Species(Base):
    __tablename__ = "species"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    scientific_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    taxonomy_source: Mapped[str] = mapped_column(String(500), default="GROE prompt taxonomy; production verification pending")
    crop_profiles: Mapped[list["CropProfile"]] = relationship(back_populates="species")

class CropProfile(Base):
    __tablename__ = "crop_profiles"
    __table_args__ = (UniqueConstraint("slug", name="uq_crop_slug"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    species_id: Mapped[str] = mapped_column(ForeignKey("species.id"), index=True)
    slug: Mapped[str] = mapped_column(String(120), index=True)
    cultivar_group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name_en: Mapped[str] = mapped_column(String(120))
    name_id: Mapped[str] = mapped_column(String(120))
    alternative_names_en: Mapped[list] = mapped_column(JSON, default=list)
    alternative_names_id: Mapped[list] = mapped_column(JSON, default=list)
    category: Mapped[str] = mapped_column(String(60), index=True)
    edible_parts: Mapped[list] = mapped_column(JSON, default=list)
    annual_or_perennial: Mapped[str] = mapped_column(String(30), default="annual")
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    guidance_en: Mapped[dict] = mapped_column(JSON, default=dict)
    guidance_id: Mapped[dict] = mapped_column(JSON, default=dict)
    source_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    verification_status: Mapped[str] = mapped_column(String(50), default="requires_agronomist_review")
    confidence_level: Mapped[str] = mapped_column(String(20), default="provisional")
    fields_requiring_review: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    species: Mapped[Species] = relationship(back_populates="crop_profiles")

class SavedPlan(Base):
    __tablename__ = "saved_plans"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160), default="My GROE Garden")
    language: Mapped[str] = mapped_column(String(5), default="en")
    planner_input: Mapped[dict] = mapped_column(JSON)
    plan_data: Mapped[dict] = mapped_column(JSON)
    share_slug: Mapped[str] = mapped_column(String(48), unique=True, index=True, default=lambda: uuid_str().replace("-", "")[:20])
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    user: Mapped[User] = relationship(back_populates="plans")
    diary_entries: Mapped[list["DiaryEntry"]] = relationship(back_populates="plan", cascade="all, delete-orphan")

class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("saved_plans.id", ondelete="CASCADE"), index=True)
    crop_profile_id: Mapped[str | None] = mapped_column(ForeignKey("crop_profiles.id"), nullable=True)
    map_zone: Mapped[str | None] = mapped_column(String(120), nullable=True)
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    growth_stage: Mapped[str | None] = mapped_column(String(80), nullable=True)
    entry_text: Mapped[str] = mapped_column(Text)
    user_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    concern_level: Mapped[str] = mapped_column(String(30), default="normal")
    detected_topics: Mapped[list] = mapped_column(JSON, default=list)
    recommended_next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped[User] = relationship(back_populates="diary_entries")
    plan: Mapped[SavedPlan] = relationship(back_populates="diary_entries")
