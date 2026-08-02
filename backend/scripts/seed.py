from app.database.session import SessionLocal
from app.database.seed import seed_crops

if __name__ == "__main__":
    with SessionLocal() as db:
        count = seed_crops(db)
        print(f"Seed complete. Inserted {count} crop profiles.")
