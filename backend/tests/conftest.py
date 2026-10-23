import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import User


@pytest.fixture()
def db_session():

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    session = TestSession()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()



def register(client, email="ana@example.com", username="ana", password="password123"):
    return client.post("/api/v1/auth/register", json={"email": email, "username": username, "password": password})



def auth_headers(client, email="ana@example.com", username="ana", password="password123"):
    register(client, email, username, password)
    token = client.post("/api/v1/auth/login", json={"username_or_email": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}



@pytest.fixture()
def make_admin(db_session):
    def _make(email):
        user = db_session.query(User).filter_by(email=email).one()
        user.role = "admin"
        db_session.commit()

    return _make
