from tests.conftest import auth_headers, register
from tests.test_recipes import PASTA


# --- US1.5: Tag validation ---
def test_tag(client):
    h = auth_headers(client)

    res = client.post(
            "/api/v1/recipes", 
            headers=h, 
            json={**PASTA, "tags": ["#italian", "#quick"]}
        )
    assert res.status_code == 201
    assert res.json()["tags"] == ["#italian", "#quick"]

    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "tags": ["#has space"]}).status_code == 422
    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "tags": [""]}).status_code == 422
    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "tags": "not-a-list"}).status_code == 422

# --- US1.5: Tag Validation (Only tests tag-specific rules) ---
def test_recipe_tag_validation(client):
    h = auth_headers(client)
    # Valid tags pass
    res = client.post("/api/v1/recipes", headers=h, json={**PASTA, "tags": ["#quick", "#dinner"]})
    assert res.status_code == 201
    # Invalid tags fail (no need to check 401 login, title, or cook_time here!)
    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "tags": ["#has spaces"]}).status_code == 422
    assert client.post("/api/v1/recipes", headers=h, json={**PASTA, "tags": [""]}).status_code == 422


# --- US1.5: Recipe Tag Query Filters (Filtering & Exclusion) ---
def test_filter_recipes_by_tag(client):
    h = auth_headers(client)
    # Seed recipes with different tags
    client.post("/api/v1/recipes", headers=h, json={**PASTA, "title": "Ramen", "tags": ["#japanese", "#latenight"]})
    client.post("/api/v1/recipes", headers=h, json={**PASTA, "title": "Udon", "tags": ["#japanese"]})
    client.post("/api/v1/recipes", headers=h, json={**PASTA, "title": "Pancakes", "tags": ["#brunch"]})
    # 1. Filter by tag (e.g., ?tag=japanese or ?tag=#japanese depending on your route)
    res = client.get("/api/v1/recipes?tag=japanese")
    assert res.status_code == 200
    titles = [r["title"] for r in res.json()]
    assert "Ramen" in titles
    assert "Udon" in titles
    assert "Pancakes" not in titles
    # 2. Filter by non-existent tag should return an empty list
    empty_res = client.get("/api/v1/recipes?tag=nonexistent")
    assert empty_res.status_code == 200
    assert empty_res.json() == []
