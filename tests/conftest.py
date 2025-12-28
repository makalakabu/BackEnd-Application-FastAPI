import pytest
import uuid
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

@pytest.fixture(autouse=True, scope="function")
def create_test_database():
    Base.metadata.drop_all(bind=engine)
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

@pytest.fixture
def create_user(client):
    def _create_user(
        username: str | None = None,
        email: str | None = None,
        password: str = "@Test1234-",
    ):
        payload = {
            "username": username or f"user_{uuid.uuid4().hex[:8]}",
            "email": email or f"user_{uuid.uuid4().hex[:8]}@test.com",
            "password": password,
        }

        res = client.post("/auth/signup", json=payload)
        assert res.status_code == 201, res.text
        return payload

    return _create_user  
    




