from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import CropProfile
from app.planning.optimizer import crop_to_dict
from app.planning.scoring import score_crop
from app.schemas.planner import PlannerInput

def test_shallow_container_is_hard_constraint(db):
    crop=db.scalar(select(CropProfile).options(selectinload(CropProfile.species)).where(CropProfile.slug=="wortel"))
    request=PlannerInput(container_depth_cm=15,surface="containers")
    result=score_crop(crop_to_dict(crop),request,2.0,{"mean_temperature_c":26})
    assert "CONTAINER_TOO_SHALLOW" in result.hard_constraints
    assert result.classification=="not_suitable"

def test_required_trellis_unavailable_is_hard_constraint(db):
    crop=db.scalar(select(CropProfile).options(selectinload(CropProfile.species)).where(CropProfile.slug=="mentimun"))
    request=PlannerInput(vertical_allowed=False)
    result=score_crop(crop_to_dict(crop),request,3.0,{"mean_temperature_c":28})
    assert "REQUIRED_SUPPORT_UNAVAILABLE" in result.hard_constraints
