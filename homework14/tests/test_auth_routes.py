import sys
from pathlib import Path
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, User
from src.database.db import get_db
from main import app

root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def client(session):
    async def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/register",
        json={"email": "test@example.com", "password": "strongpassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login(client, session):
    user = User(email="user@example.com", hashed_password="$2b$12$KxsqLJpo3CwD/4uJYRXY5OzUjmFwh6owSu3Z4RjIj2kP3wr.7LkE6")  # bcrypt hash for "password"
    session.add(user)
    session.commit()
    response = await client.post(
        "/login",
        json={"email": "user@example.com", "password": "password"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
