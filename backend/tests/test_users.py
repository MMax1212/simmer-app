from tests.conftest import auth_headers


# --- US1.3: User Profile Management (Profile Partial Update & Persistence) ---
def test_update_profile_partial(client):
    h = auth_headers(client)
    res = client.put("/api/v1/users/me", headers=h, json={"bio": "I love pasta", "culinary_preferences": ["vegan", "gluten-free"]})
    assert res.status_code == 200
    assert res.json()["culinary_preferences"] == ["gluten-free", "vegan"]

    # Sending only avatar_url must not wipe the bio.
    res = client.put("/api/v1/users/me", headers=h, json={"avatar_url": "https://example.com/a.png"})
    assert res.json()["bio"] == "I love pasta"


# --- US1.3: User Profile Management (Input Validation on Preferences) ---
def test_blank_culinary_preference_rejected(client):
    h = auth_headers(client)
    assert client.put("/api/v1/users/me", headers=h, json={"culinary_preferences": [" "]}).status_code == 422


# --- US1.3: User Profile Management (Public Profile Privacy - Hiding Email) ---
def test_public_profile_hides_email(client):
    auth_headers(client)
    res = client.get("/api/v1/users/ana")
    assert res.status_code == 200 and "email" not in res.json()
    assert client.get("/api/v1/users/nobody").status_code == 404


# --- US1.2: Admin Account & RBAC (Admin Endpoints Authorization & Deactivation) ---
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
    # Deactivated users are locked out.
    assert client.get("/api/v1/auth/me", headers=user_h).status_code == 401
    login = client.post("/api/v1/auth/login", json={"username_or_email": "ana@example.com", "password": "password123"})
    assert login.status_code == 403
