from tests.conftest import auth_headers


def test_admin_endpoints(client, make_admin):
    user_h = auth_headers(client)
    assert client.get("/api/v1/admin/users", headers=user_h).status_code == 403

    admin_h = auth_headers(client, email="boss@example.com", username="boss")
    make_admin("boss@example.com")
    users = client.get("/api/v1/admin/users", headers=admin_h).json()
    assert len(users) == 2

    ana_id = next(u["id"] for u in users if u["username"] == "ana")
    res = client.patch(f"/api/v1/admin/users/{ana_id}/status", headers=admin_h, json={"is_active": False})
    assert res.json()["is_active"] is False

    assert client.get("/api/v1/auth/me", headers=user_h).status_code == 401
    login = client.post("/api/v1/auth/login", json={"username_or_email": "ana@example.com", "password": "password123"})
    assert login.status_code == 403
