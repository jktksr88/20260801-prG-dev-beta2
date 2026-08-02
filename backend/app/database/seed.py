from __future__ import annotations
import json
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Species, CropProfile

SEED_PATH = Path(__file__).resolve().parents[2] / "seed_data" / "crops.json"

def seed_crops(db: Session) -> int:
    rows = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    if len(rows) != 50:
        raise RuntimeError("GROE seed must contain exactly 50 crop profiles")
    existing = {x for x, in db.execute(select(CropProfile.slug)).all()}
    inserted = 0
    for row in rows:
        if row["slug"] in existing:
            continue
        species = db.scalar(select(Species).where(Species.scientific_name == row["scientific_name"]))
        if not species:
            species = Species(scientific_name=row["scientific_name"], taxonomy_source=row["source_metadata"]["taxonomy_source"])
            db.add(species); db.flush()
        data = dict(row)
        data.pop("scientific_name")
        db.add(CropProfile(species_id=species.id, **data))
        inserted += 1
    db.commit()
    active_count = db.scalar(select(func.count()).select_from(CropProfile).where(CropProfile.active.is_(True)))
    if active_count != 50:
        raise RuntimeError(f"Expected exactly 50 active crop profiles, found {active_count}")
    return inserted
