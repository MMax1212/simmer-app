from tests.conftest import auth_headers, register


def test_register_returns_user_without_password(client):
    res = register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "ana" and body["role"] == "user"
    assert "password" not in body and "hashed_password" not in body


def test_duplicate_email_and_username_rejected(client):
    register(client)
    assert register(client, username="other").status_code == 409
    assert register(client, email="other@example.com", username="ANA").status_code == 409


def test_invalid_input_rejected(client):
    assert register(client, email="not-an-email").status_code == 422
    assert register(client, password="short").status_code == 422
    assert register(client, username="bad name!").status_code == 422


def test_login_success_and_failure(client):
    register(client)
    ok = client.post("/api/v1/auth/login", json={"username_or_email": "ANA@example.com", "password": "password123"})
    assert ok.status_code == 200 and ok.json()["access_token"]
    bad = client.post("/api/v1/auth/login", json={"username_or_email": "ana@example.com", "password": "wrongpass1"})
    assert bad.status_code == 401
    missing = client.post("/api/v1/auth/login", json={"username_or_email": "nobody@example.com", "password": "password123"})
    assert missing.status_code == 401


def test_swagger_form_login(client):
    register(client)
    res = client.post("/api/v1/auth/token", data={"username": "ana@example.com", "password": "password123"})
    assert res.status_code == 200


def test_me_requires_valid_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    res = client.get("/api/v1/auth/me", headers=auth_headers(client))
    assert res.status_code == 200 and res.json()["email"] == "ana@example.com"
