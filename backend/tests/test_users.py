from tests.conftest import auth_headers


def test_update_profile_partial(client):
    h = auth_headers(client)
    res = client.patch("/api/users/me", headers=h, json={"bio": "I love pasta", "dietary_prefs": ["vegan", "gluten-free"]})
    assert res.status_code == 200
    assert res.json()["dietary_prefs"] == ["gluten-free", "vegan"]

    # Sending only avatar_url must not wipe the bio.
    res = client.patch("/api/users/me", headers=h, json={"avatar_url": "https://example.com/a.png"})
    assert res.json()["bio"] == "I love pasta"


def test_unknown_dietary_pref_rejected(client):
    h = auth_headers(client)
    assert client.patch("/api/users/me", headers=h, json={"dietary_prefs": ["carnivore-only"]}).status_code == 422


def test_public_profile_hides_email(client):
    auth_headers(client)
    res = client.get("/api/users/ana")
    assert res.status_code == 200 and "email" not in res.json()
    assert client.get("/api/users/nobody").status_code == 404


def test_admin_endpoints(client, make_admin):
    user_h = auth_headers(client)
    assert client.get("/api/admin/users", headers=user_h).status_code == 403

    admin_h = auth_headers(client, email="boss@example.com", username="boss")
    make_admin("boss@example.com")
    users = client.get("/api/admin/users", headers=admin_h).json()
    assert len(users) == 2

    ana_id = next(u["id"] for u in users if u["username"] == "ana")
    res = client.patch(f"/api/admin/users/{ana_id}", headers=admin_h, json={"is_active": False})
    assert res.json()["is_active"] is False
    # Deactivated users are locked out.
    assert client.get("/api/users/me", headers=user_h).status_code == 401
    login = client.post("/api/auth/login", json={"email": "ana@example.com", "password": "password123"})
    assert login.status_code == 403
