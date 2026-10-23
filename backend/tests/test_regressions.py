from datetime import datetime, timedelta, timezone


import bcrypt


import jwt


import pytest


from app.core.config import settings


from app.models import AdminAudit, User


from tests.conftest import auth_headers, register


@pytest.mark.parametrize("password", ["😀" * 20, "x" * 73, "é" * 72])
def test_unicode_and_long_passwords_can_register_and_login(client, password):
    assert register(client, password=password).status_code == 201
    res = client.post("/api/v1/auth/login", json={"username_or_email": "ANA", "password": password})
    assert res.status_code == 200
    assert res.json()["user"]["username"] == "ana"
    assert password not in res.text
    assert client.post("/api/v1/auth/login", json={
        "username_or_email": "ana", "password": "wrong" * 30}).status_code == 401


@pytest.mark.parametrize("payload", [
    {"email": "secret@example.com", "username": "secretuser", "password": "sh0rt!"},
    {"email": "bad", "username": "secretuser", "password": "super-secret-password"},
])
def test_validation_errors_never_echo_passwords(client, payload):
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422
    assert payload["password"] not in res.text
    assert all(set(error) <= {"loc", "msg", "type"} for error in res.json()["detail"])


def test_missing_login_field_does_not_echo_request_body(client):
    res = client.post("/api/v1/auth/login", json={"password": "private-password"})
    assert res.status_code == 422 and "private-password" not in res.text


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


def test_admin_reactivation_roles_audit_and_self_protection(client, make_admin, db_session):
    user_h = auth_headers(client)
    admin_h = auth_headers(client, email="boss@example.com", username="boss")
    make_admin("boss@example.com")
    users = client.get("/api/v1/admin/users", headers=admin_h).json()
    uid = next(u["id"] for u in users if u["username"] == "ana")
    aid = next(u["id"] for u in users if u["username"] == "boss")
    path = f"/api/v1/admin/users/{uid}/status"
    assert client.patch(path, headers=admin_h, json={"is_active": False}).status_code == 200
    assert client.get("/api/v1/auth/me", headers=user_h).status_code == 401
    assert client.patch(path, headers=admin_h, json={"is_active": True}).status_code == 200
    assert client.get("/api/v1/auth/me", headers=user_h).status_code == 200
    assert client.patch(path, headers=admin_h, json={"role": "admin"}).status_code == 200
    assert client.get("/api/v1/admin/users", headers=user_h).status_code == 200
    assert db_session.query(AdminAudit).count() == 3
    assert client.patch(path, headers=admin_h, json={"is_active": None}).status_code == 422
    assert client.patch(f"/api/v1/admin/users/{aid}/status", headers=admin_h, json={"role": "user"}).status_code == 400
    assert client.patch("/api/v1/admin/users/99999/status", headers=admin_h, json={"is_active": False}).status_code == 404
