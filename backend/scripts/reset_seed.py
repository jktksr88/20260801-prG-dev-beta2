from sqlalchemy import delete
from app.database.session import SessionLocal
from app.models import CropProfile, Species
from app.database.seed import seed_crops

if __name__ == "__main__":
    with SessionLocal() as db:
        db.execute(delete(CropProfile)); db.execute(delete(Species)); db.commit()
        print(f"Reset complete. Inserted {seed_crops(db)} crop profiles.")
