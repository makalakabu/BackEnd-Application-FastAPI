import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from db.db_base import Base
from main import app
from api.deps import get_db


DATABASE_TEST_URL = "sqlite:///./test.db"
engine = create_engine(
    DATABASE_TEST_URL,
    connect_args={"check_same_thread": False},  # SQLite only
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

@pytest.fixture(autouse=True, scope="session")
def create_test_database():
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    




