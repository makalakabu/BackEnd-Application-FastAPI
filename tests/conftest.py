import pytest
import uuid
import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from fastapi.testclient import TestClient

from db.db_base import Base
from main import app
from api.deps import get_db


DATABASE_TEST_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

connect_args = {}
if DATABASE_TEST_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    DATABASE_TEST_URL,
    connect_args=connect_args, 
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

@pytest.fixture
def login_user(client, create_user):
    def _login_user(user: dict | None = None):
        if user is None:
            user = create_user()

        res = client.post(
            "/auth/login",
            json={
                "email": user["email"],
                "password": user["password"]
            }
        )
        assert res.status_code == 200

        token = res.json()["access_token"]
        assert token

        return user, {"Authorization": f"Bearer {token}"}
    return _login_user

    




