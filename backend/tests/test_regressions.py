from datetime import datetime, timedelta, timezone
from copy import deepcopy

import bcrypt
import jwt
import pytest

from app.core.config import settings
from app.models import AdminAudit, RecipeStep, User
from tests.conftest import auth_headers, register
from tests.test_recipes import PASTA


# --- US1.1: Password Security (Unicode & Long Password Hashing Support) ---
@pytest.mark.parametrize("password", ["😀" * 20, "x" * 73, "é" * 72])
def test_unicode_and_long_passwords_can_register_and_login(client, password):
    assert register(client, password=password).status_code == 201
    res = client.post("/api/v1/auth/login", json={"username_or_email": "ANA", "password": password})
    assert res.status_code == 200
    assert res.json()["user"]["username"] == "ana"
    assert password not in res.text
    assert client.post("/api/v1/auth/login", json={
        "username_or_email": "ana", "password": "wrong" * 30}).status_code == 401


# --- US1.1: Security & Privacy (Passwords Never Echoed in Validation Errors) ---
@pytest.mark.parametrize("payload", [
    {"email": "secret@example.com", "username": "secretuser", "password": "sh0rt!"},
    {"email": "bad", "username": "secretuser", "password": "super-secret-password"},
])
def test_validation_errors_never_echo_passwords(client, payload):
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422
    assert payload["password"] not in res.text
    assert all(set(error) <= {"loc", "msg", "type"} for error in res.json()["detail"])


# --- US1.1: Security & Privacy (Login Request Body Not Leaked in Validation Errors) ---
def test_missing_login_field_does_not_echo_request_body(client):
    res = client.post("/api/v1/auth/login", json={"password": "private-password"})
    assert res.status_code == 422 and "private-password" not in res.text


# --- US1.1: Password Migration (Upgrade Legacy Bcrypt to Argon2 on Login) ---
def test_existing_bcrypt_account_upgrades_without_losing_access(client, db_session):
    register(client)
    user = db_session.query(User).one()
    user.hashed_password = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
    db_session.commit()
    assert client.post("/api/v1/auth/login", json={
        "username_or_email": "ana", "password": "x" * 73}).status_code == 401
    assert client.post("/api/v1/auth/login", json={
        "username_or_email": "ana@example.com", "password": "password123"}).status_code == 200
    assert user.hashed_password.startswith("$argon2")

# --- US1.1 & US1.2: Security (Expired Token 401 & Role Escalation Rejection) ---
def test_expired_tokens_and_role_escalation_are_rejected(client):
    h = auth_headers(client)
    user_id = client.get("/api/v1/auth/me", headers=h).json()["id"]
    expired = jwt.encode({"sub": str(user_id), "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
                         settings.secret_key, algorithm=settings.algorithm)
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    assert client.patch(f"/api/v1/admin/users/{user_id}/status", headers=h, json={"role": "admin"}).status_code == 403
    assert register(client, email="new@example.com", username="new").status_code == 201
    assert client.post("/api/v1/auth/register", json={
        "email": "bad@example.com", "username": "bad", "password": "password123", "role": "admin"}).status_code == 422

# --- US1.1, US1.3, US1.4, US1.5: End-to-End Vertical Slice Integration Flow ---
def test_onboarding_profile_recipe_library_flow(client):
    assert register(client).status_code == 201
    login = client.post("/api/v1/auth/login", json={"username_or_email": "ana", "password": "password123"})
    assert login.status_code == 200 and login.json()["token_type"] == "bearer"
    h = {"Authorization": "Bearer " + login.json()["access_token"]}
    assert client.put("/api/v1/users/me", headers=h, json={"bio": "Home cook"}).json()["bio"] == "Home cook"
    assert client.get("/api/v1/recipes/my-recipes", headers=h).json() == []
    created = client.post("/api/v1/recipes", headers=h, json=PASTA)
    assert created.status_code == 201
    assert client.get("/api/v1/recipes/my-recipes", headers=h).json()[0]["id"] == created.json()["id"]
    assert client.get("/api/health").json()["status"] == "ok"
