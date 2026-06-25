from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.role import Role
from app.models.todo import Todo
from app.models.user import User
from app.schemas.auth.request import TokenData
from app.services.auth_services import ADMIN_ROLE_NAME, DEFAULT_ROLE_NAME, get_password_hash


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash=get_password_hash("password123"),
    )


@pytest.fixture(scope="function")
def admin_user():
    return User(
        id=uuid4(),
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=get_password_hash("adminpassword123"),
    )


@pytest.fixture(scope="function")
def test_token_data(test_user):
    return TokenData(user_id=str(test_user.id))


@pytest.fixture(scope="function")
def test_todo(test_token_data):
    return Todo(
        id=uuid4(),
        description="Test Description",
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        user_id=test_token_data.get_uuid(),
    )


@pytest.fixture(scope="function")
def client(db_session):
    for role_name in (DEFAULT_ROLE_NAME, ADMIN_ROLE_NAME):
        if not db_session.query(Role).filter(Role.name == role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    response = client.post(
        "/auth/",
        json={
            "email": "test.user@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/token",
        data={
            "username": "test.user@example.com",
            "password": "testpassword123",
            "grant_type": "password",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(client, db_session, admin_user):
    admin_role = db_session.query(Role).filter(Role.name == ADMIN_ROLE_NAME).first()
    admin_user.roles.append(admin_role)
    db_session.add(admin_user)
    db_session.commit()

    response = client.post(
        "/auth/token",
        data={
            "username": "admin@example.com",
            "password": "adminpassword123",
            "grant_type": "password",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
