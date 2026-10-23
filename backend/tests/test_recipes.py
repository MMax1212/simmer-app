from tests.conftest import auth_headers

# --- US1.4 & US1.5: Recipe Creation & Detail Display Test Fixture ---
PASTA = {
    "title": "Tomato Pasta",
    "description": "Weeknight classic",
    "steps": [{"step_number": 1, "instruction": "Boil pasta"}, {"step_number": 2, "instruction": "Make sauce"}, {"step_number": 3, "instruction": "Combine"}],
    "prep_time_mins": 10,
    "cook_time_mins": 20,
    "servings": 4,
    "ingredients": [
        {"name": "spaghetti", "amount": 400, "unit": "g"},
        {"name": "canned tomatoes", "amount": 1, "unit": "can"},
        {"name": "salt", "amount": 1, "unit": "pinch"},
    ],
}


# --- US1.4 & US1.5: Create Recipe & Read Recipe by ID (HTTP 201 & 404) ---
def test_create_and_read_recipe(client):
    h = auth_headers(client)
    res = client.post("/api/v1/recipes", headers=h, json=PASTA)
    assert res.status_code == 201
    recipe = res.json()
    assert recipe["author_username"] == "ana"
    assert [i["name"] for i in recipe["ingredients"]] == ["spaghetti", "canned tomatoes", "salt"]

    assert client.get(f"/api/v1/recipes/{recipe['id']}").json()["title"] == "Tomato Pasta"
    assert client.get("/api/v1/recipes/9999").status_code == 404


# --- US1.4: Recipe Creation (Auth Enforcement & Validation Rules) ---
def test_create_requires_login_and_valid_data(client):
    assert client.post("/api/v1/recipes", json=PASTA).status_code == 401
    h = auth_headers(client)
    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "title": ""}).status_code == 422
    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "cook_time_mins": -5}).status_code == 422


# --- US1.4: Recipe Creation & Saving (Full Update & Ingredient Replacement) ---
def test_update_replaces_ingredients(client):
    h = auth_headers(client)
    rid = client.post("/api/v1/recipes", headers=h, json=PASTA).json()["id"]
    res = client.put(f"/api/v1/recipes/{rid}", headers=h, json={**PASTA, "title": "Better Pasta", "ingredients": [{"name": "penne", "amount": 100, "unit": "g"}]})
    assert res.status_code == 200
    assert res.json()["title"] == "Better Pasta"
    assert [i["name"] for i in res.json()["ingredients"]] == ["penne"]


# --- US1.4 & US1.5: Recipe Permissions (Author-Only Edit and Deletion - HTTP 403 & 204) ---
def test_only_owner_can_edit_or_delete(client):
    owner = auth_headers(client)
    rid = client.post("/api/v1/recipes", headers=owner, json=PASTA).json()["id"]
    other = auth_headers(client, email="bob@example.com", username="bob")
    assert client.put(f"/api/v1/recipes/{rid}", headers=other, json=PASTA).status_code == 403
    assert client.delete(f"/api/v1/recipes/{rid}", headers=other).status_code == 403
    assert client.delete(f"/api/v1/recipes/{rid}", headers=owner).status_code == 204
    assert client.get(f"/api/v1/recipes/{rid}").status_code == 404


# --- US1.5: Personal Recipe Tab (Author Isolation & Chronological Order) ---
def test_my_recipes_only_shows_mine_newest_first(client):
    ana = auth_headers(client)
    bob = auth_headers(client, email="bob@example.com", username="bob")
    client.post("/api/v1/recipes", headers=ana, json={**PASTA, "title": "First"})
    client.post("/api/v1/recipes", headers=ana, json={**PASTA, "title": "Second"})
    client.post("/api/v1/recipes", headers=bob, json={**PASTA, "title": "Bob's"})
    titles = [r["title"] for r in client.get("/api/v1/recipes/my-recipes", headers=ana).json()]
    assert titles == ["Second", "First"]
