from tests.conftest import auth_headers

PASTA = {
    "title": "Tomato Pasta",
    "description": "Weeknight classic",
    "instructions": "1. Boil pasta.\n2. Make sauce.\n3. Combine.",
    "prep_time_mins": 10,
    "cook_time_mins": 20,
    "servings": 4,
    "ingredients": [
        {"name": "spaghetti", "quantity": 400, "unit": "g"},
        {"name": "canned tomatoes", "quantity": 1, "unit": "can"},
        {"name": "salt"},
    ],
}


def test_create_and_read_recipe(client):
    h = auth_headers(client)
    res = client.post("/api/recipes", headers=h, json=PASTA)
    assert res.status_code == 201
    recipe = res.json()
    assert recipe["owner_username"] == "ana"
    assert [i["name"] for i in recipe["ingredients"]] == ["spaghetti", "canned tomatoes", "salt"]

    assert client.get(f"/api/recipes/{recipe['id']}").json()["title"] == "Tomato Pasta"
    assert client.get("/api/recipes/9999").status_code == 404


def test_create_requires_login_and_valid_data(client):
    assert client.post("/api/recipes", json=PASTA).status_code == 401
    h = auth_headers(client)
    assert client.post("/api/recipes", headers=h, json={**PASTA, "title": ""}).status_code == 422
    assert client.post("/api/recipes", headers=h, json={**PASTA, "cook_time_mins": -5}).status_code == 422


def test_update_replaces_ingredients(client):
    h = auth_headers(client)
    rid = client.post("/api/recipes", headers=h, json=PASTA).json()["id"]
    res = client.put(f"/api/recipes/{rid}", headers=h, json={**PASTA, "title": "Better Pasta", "ingredients": [{"name": "penne"}]})
    assert res.status_code == 200
    assert res.json()["title"] == "Better Pasta"
    assert [i["name"] for i in res.json()["ingredients"]] == ["penne"]


def test_only_owner_can_edit_or_delete(client):
    owner = auth_headers(client)
    rid = client.post("/api/recipes", headers=owner, json=PASTA).json()["id"]
    other = auth_headers(client, email="bob@example.com", username="bob")
    assert client.put(f"/api/recipes/{rid}", headers=other, json=PASTA).status_code == 403
    assert client.delete(f"/api/recipes/{rid}", headers=other).status_code == 403
    assert client.delete(f"/api/recipes/{rid}", headers=owner).status_code == 204
    assert client.get(f"/api/recipes/{rid}").status_code == 404


def test_my_recipes_only_shows_mine_newest_first(client):
    ana = auth_headers(client)
    bob = auth_headers(client, email="bob@example.com", username="bob")
    client.post("/api/recipes", headers=ana, json={**PASTA, "title": "First"})
    client.post("/api/recipes", headers=ana, json={**PASTA, "title": "Second"})
    client.post("/api/recipes", headers=bob, json={**PASTA, "title": "Bob's"})
    titles = [r["title"] for r in client.get("/api/users/me/recipes", headers=ana).json()]
    assert titles == ["Second", "First"]
