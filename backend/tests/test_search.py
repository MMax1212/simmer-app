from tests.conftest import auth_headers

# -- US2.2 Task 2.1: EndPoint Exists & Returns 200 ---
def test_search_empty_database(client):
    res = client.get("/api/v1/recipes")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []

PASTA_RECIPE = {
    "title": "Rustic Tomato Pasta",
    "description": "Hearty Italian dinner with fresh basil and garlic.",
    "cuisine": "Italian",
    "meal_type": "dinner",
    "difficulty": "easy",
    "cook_time_mins": 25,
    "prep_time_mins": 10,
    "servings": 2,
    "ingredients": [
        {"name": "spaghetti", "amount": 200, "unit": "g"},
        {"name": "garlic clove", "amount": 3, "unit": "count"},
        {"name": "crushed tomatoes", "amount": 400, "unit": "g"},
    ],
    "steps": [
        {"step_number": 1, "instruction": "Boil spaghetti in salted water."},
        {"step_number": 2, "instruction": "Sauté minced garlic and simmer with tomatoes."},
    ],
}

TACO_RECIPE = {
    "title": "Spicy Street Tacos",
    "description": "Authentic Mexican tacos with salsa verde and cilantro.",
    "cuisine": "Mexican",
    "meal_type": "lunch",
    "difficulty": "medium",
    "cook_time_mins": 15,
    "prep_time_mins": 15,
    "servings": 3,
    "ingredients": [
        {"name": "corn tortillas", "amount": 6, "unit": "count"},
        {"name": "flank steak", "amount": 300, "unit": "g"},
        {"name": "cilantro", "amount": 1, "unit": "bunch"},
    ],
    "steps": [
        {"step_number": 1, "instruction": "Grill steak to desired doneness."},
        {"step_number": 2, "instruction": "Warm tortillas and assemble tacos."},
    ],
}

# --- US2.2: Test 1: Empty Database --- 
def test_search_empty_database(client):
    res = client.get("/api/v1/recipes")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []

# --- US2.2: Search by Keyword & Case-Insensitve ---
def test_search_by_keyword_and_case_insensitive(client):
    headers = auth_headers(client)
    client.post("/api/v1/recipes", headers=headers, json=PASTA_RECIPE)
    client.post("/api/v1/recipes", headers=headers, json=TACO_RECIPE)
    # Lowercase search: "pasta" matches title
    res_lower = client.get("/api/v1/recipes?q=pasta")
    assert res_lower.status_code == 200
    items = res_lower.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Rustic Tomato Pasta"
    # Uppercase search: "PASTA" should match the same (case-insensitive)
    res_upper = client.get("/api/v1/recipes?q=PASTA")
    assert res_upper.status_code == 200
    assert len(res_upper.json()["items"]) == 1
    # Description search: "basil" appears only in the pasta description
    res_desc = client.get("/api/v1/recipes?q=basil")
    assert res_desc.status_code == 200
    assert len(res_desc.json()["items"]) == 1
    # Non-matching search: "sushi" returns 0 items
    res_none = client.get("/api/v1/recipes?q=sushi")
    assert res_none.status_code == 200
    assert res_none.json()["total"] == 0
    assert res_none.json()["items"] == []

# --- US2.2: Test 3: Search by Specific Ingredient ---
def test_search_by_ingredient(client):
    headers = auth_headers(client)
    client.post("/api/v1/recipes", headers=headers, json=PASTA_RECIPE)
    client.post("/api/v1/recipes", headers=headers, json=TACO_RECIPE)

    # Search via ingredient parameter -> "garlic" is only in Pasta
    res = client.get("/api/v1/recipes?ingredient=garlic")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Rustic Tomato Pasta"


# --- US2.2: Test 4: Faceted Filtering (Cuisine, Difficulty, and Mismatch) ---
def test_search_faceted_filtering(client):
    headers = auth_headers(client)
    client.post("/api/v1/recipes", headers=headers, json=PASTA_RECIPE)
    client.post("/api/v1/recipes", headers=headers, json=TACO_RECIPE)

    # 1. Filter by cuisine
    res_cuisine = client.get("/api/v1/recipes?cuisine=Italian")
    assert res_cuisine.status_code == 200
    assert len(res_cuisine.json()["items"]) == 1
    assert res_cuisine.json()["items"][0]["title"] == "Rustic Tomato Pasta"

    # 2. Filter by difficulty
    res_diff = client.get("/api/v1/recipes?difficulty=medium")
    assert res_diff.status_code == 200
    assert len(res_diff.json()["items"]) == 1
    assert res_diff.json()["items"][0]["title"] == "Spicy Street Tacos"

    # 3. Combine facets that do not intersect -> should return 0 results
    res_no_match = client.get("/api/v1/recipes?cuisine=Italian&difficulty=hard")
    assert res_no_match.status_code == 200
    assert res_no_match.json()["total"] == 0

    # --- US2.2: Test 5: Pagination Verification ---
def test_search_pagination(client):
    headers = auth_headers(client)
    client.post("/api/v1/recipes", headers=headers, json=PASTA_RECIPE)
    client.post("/api/v1/recipes", headers=headers, json=TACO_RECIPE)

    # Page 1: limit=1, offset=0
    res_page1 = client.get("/api/v1/recipes?limit=1&offset=0")
    assert res_page1.status_code == 200
    data1 = res_page1.json()
    assert data1["total"] == 2
    assert len(data1["items"]) == 1
    assert data1["limit"] == 1
    assert data1["offset"] == 0

    # Page 2: limit=1, offset=1
    res_page2 = client.get("/api/v1/recipes?limit=1&offset=1")
    assert res_page2.status_code == 200
    data2 = res_page2.json()
    assert data2["total"] == 2
    assert len(data2["items"]) == 1
    # Verify page 1 and page 2 returned different recipes
    assert data1["items"][0]["id"] != data2["items"][0]["id"]


# --- US2.2: Test 6: Parameter Validation Guardrails (HTTP 422) ---
def test_search_parameter_validation_guardrails(client):
    # limit > 100 must be rejected
    assert client.get("/api/v1/recipes?limit=101").status_code == 422
    # limit < 1 must be rejected
    assert client.get("/api/v1/recipes?limit=0").status_code == 422
    # offset < 0 must be rejected
    assert client.get("/api/v1/recipes?offset=-1").status_code == 422
    # query exceeding 100 characters must be rejected
    assert client.get(f"/api/v1/recipes?q={'a'*101}").status_code == 422


# --- US2.2: Test 7: SQL Injection Prevention Guardrail ---
def test_search_sql_injection_defense(client):
    headers = auth_headers(client)
    client.post("/api/v1/recipes", headers=headers, json=PASTA_RECIPE)

    # Attempt classic SQL injection payload
    injection_payload = "' OR 1=1 --"
    res = client.get(f"/api/v1/recipes?q={injection_payload}")
    assert res.status_code == 200
    assert res.json()["total"] == 0
    assert res.json()["items"] == []