from sqlalchemy import select, func
from app.models import CropProfile
from app.database.seed import seed_crops

def test_seed_has_exactly_50_and_is_idempotent(db):
    assert db.scalar(select(func.count()).select_from(CropProfile).where(CropProfile.active.is_(True)))==50
    assert seed_crops(db)==0
    assert db.scalar(select(func.count()).select_from(CropProfile))==50

def test_all_profiles_are_bilingual_and_governed(db):
    rows=db.scalars(select(CropProfile)).all()
    assert all(x.name_en and x.name_id and x.guidance_en and x.guidance_id for x in rows)
    assert all(x.verification_status in {"verified","provisionally_sourced","requires_agronomist_review"} for x in rows)
