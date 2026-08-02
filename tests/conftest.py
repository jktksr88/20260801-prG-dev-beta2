import os
from pathlib import Path
os.environ["DATABASE_URL"]="sqlite:///./test_groe.db"
os.environ["JWT_SECRET"]="test-secret-at-least-long-enough"
os.environ["AUTO_SEED"]="false"
import pytest
from fastapi.testclient import TestClient
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.database.seed import seed_crops
from app.main import app

@pytest.fixture(scope="session",autouse=True)
def database():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine)
    with SessionLocal() as db: seed_crops(db)
    yield
    Base.metadata.drop_all(engine)
    Path("test_groe.db").unlink(missing_ok=True)

@pytest.fixture()
def db():
    with SessionLocal() as session: yield session

@pytest.fixture()
def client():
    with TestClient(app) as c: yield c
