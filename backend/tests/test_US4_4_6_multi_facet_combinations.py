"""Comprehensive Combinatorial Matrix & Strict Exclusion Tests for US4.4 (Task 4.4.6).

Verifies the full multi-facet query engine, strict boolean intersections,
exclusion logic, SQL duplicate trap avoidance, and null-time safety.
"""
from tests.conftest import auth_headers


BASE_RECIPE = {
    "title": "Base Dish",
    "description": "Standard recipe template for combinatorial testing",
    "steps": [{"step_number": 1, "instruction": "Cook thoroughly and serve"}],
    "prep_time_mins": 10,
    "cook_time_mins": 15,
    "servings": 2,
    "ingredients": [
        {"name": "olive oil", "amount": 1, "unit": "tbsp"},
        {"name": "garlic", "amount": 2, "unit": "count"},
        {"name": "salt", "amount": 1, "unit": "pinch"},
    ],
}


def _create(client, headers, title, tags=None, cuisine="Italian", meal_type="dinner", prep=10, cook=15, desc=None):
    payload = {
        **BASE_RECIPE,
        "title": title,
        "description": desc or BASE_RECIPE["description"],
        "tags": tags or [],
        "cuisine": cuisine,
        "meal_type": meal_type,
        "prep_time_mins": prep,
        "cook_time_mins": cook,
    }
    res = client.post("/api/v1/recipes", headers=headers, json=payload)
    assert res.status_code == 201, f"Failed to create recipe '{title}': {res.text}"
    return res.json()


def test_US4_4_6_multi_dietary_strict_and_intersection(client):
    """AC1: Multi-dietary queries require recipes to possess ALL requested dietary tags."""
    h = auth_headers(client, email="matrix1@example.com", username="matrix1")

    # Triple match
    _create(client, h, "Triple Clean Bowl", tags=["#vegan", "#gluten-free", "#keto"])
    # Dual match only
    _create(client, h, "Vegan GF Pasta", tags=["#vegan", "#gluten-free"])
    # Single match only
    _create(client, h, "Keto Ribeye", tags=["#keto"])

    # Query requires ALL 3
    res = client.get("/api/v1/recipes?dietary=vegan,gluten-free,keto")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Triple Clean Bowl"


def test_US4_4_6_simultaneous_multi_facet_intersection(client):
    """AC2: Simultaneous constraints (text, cuisine, meal_type, dietary, occasion, max_time)

    must evaluate as a strict boolean intersection.
    """
    h = auth_headers(client, email="matrix2@example.com", username="matrix2")

    # Recipe A: Matches EVERY facet
    _create(
        client,
        h,
        "Spicy Garlic Tofu",
        cuisine="Asian",
        meal_type="dinner",
        tags=["#vegan", "#gluten-free", "#quick-dinner"],
        prep=10,
        cook=15,  # Total 25 <= 30
    )

    # Recipe B: Matches everything except cook time exceeds max_time
    _create(
        client,
        h,
        "Slow Garlic Tofu Stew",
        cuisine="Asian",
        meal_type="dinner",
        tags=["#vegan", "#gluten-free", "#quick-dinner"],
        prep=15,
        cook=25,  # Total 40 > 30
    )

    # Recipe C: Matches everything except cuisine is Italian
    _create(
        client,
        h,
        "Italian Garlic Tofu",
        cuisine="Italian",
        meal_type="dinner",
        tags=["#vegan", "#gluten-free", "#quick-dinner"],
        prep=10,
        cook=15,
    )

    # Recipe D: Matches everything except lacks #gluten-free
    _create(
        client,
        h,
        "Soy Sauce Garlic Tofu",
        cuisine="Asian",
        meal_type="dinner",
        tags=["#vegan", "#quick-dinner"],
        prep=10,
        cook=15,
    )

    # Recipe E: Matches everything except lacks occasion #quick-dinner
    _create(
        client,
        h,
        "Weekend Garlic Tofu",
        cuisine="Asian",
        meal_type="dinner",
        tags=["#vegan", "#gluten-free"],
        prep=10,
        cook=15,
    )

    # Query with all facets simultaneously active
    res = client.get(
        "/api/v1/recipes?q=Garlic&cuisine=Asian&meal_type=dinner&dietary=vegan,gluten-free&occasion=quick-dinner&max_time=30"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Spicy Garlic Tofu"


def test_US4_4_6_strict_vegetarian_vs_vegan_exclusion(client):
    """AC3: A dish tagged #vegetarian must NOT match a query filtering for #vegan."""
    h = auth_headers(client, email="matrix3@example.com", username="matrix3")

    _create(client, h, "Cheese Quesadilla", tags=["#vegetarian"])
    _create(client, h, "Bean Burrito", tags=["#vegan"])

    res = client.get("/api/v1/recipes?dietary=vegan")
    assert res.status_code == 200
    titles = [r["title"] for r in res.json()["items"]]
    assert "Bean Burrito" in titles
    assert "Cheese Quesadilla" not in titles


def test_US4_4_6_sql_duplicate_trap_avoidance_with_pagination(client):
    """AC4: Joining multiple tags must never create duplicate SQL rows or corrupt total count."""
    h = auth_headers(client, email="matrix4@example.com", username="matrix4")

    # Dish with 6 tags
    _create(
        client,
        h,
        "Super Tagged Salad",
        tags=["#vegan", "#gluten-free", "#keto", "#quick-dinner", "#meal-prep", "#comfort-food"],
    )

    res = client.get("/api/v1/recipes?dietary=vegan,gluten-free,keto&occasion=quick-dinner&limit=10&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Super Tagged Salad"


def test_US4_4_6_zero_prep_and_coalesce_time_handling(client):
    """AC5: Recipes with 0 or minimal prep time correctly calculate total cook duration."""
    h = auth_headers(client, email="matrix5@example.com", username="matrix5")
    _create(client, h, "Zero Prep Fast Dish", tags=["#comfort-food"], prep=0, cook=20)
    _create(client, h, "Standard Prep Dish", tags=["#comfort-food"], prep=10, cook=20)

    # Total time 20 <= 25: matches "Zero Prep Fast Dish", excludes "Standard Prep Dish" (total 30)
    res = client.get("/api/v1/recipes?occasion=comfort-food&max_time=25")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Zero Prep Fast Dish" in titles
    assert "Standard Prep Dish" not in titles


def test_US4_4_6_whitespace_casing_and_hash_prefix_normalization(client):
    """AC1, AC2: Tolerates leading/trailing whitespace, uppercase, and optional # prefixes."""
    h = auth_headers(client, email="matrix6@example.com", username="matrix6")
    _create(client, h, "Crispy Tofu Bites", tags=["#vegan", "#quick-dinner"])

    res = client.get("/api/v1/recipes?dietary=%20%20VEGAN%20%20&occasion=%20%20#QUICK-DINNER%20%20")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Crispy Tofu Bites"
