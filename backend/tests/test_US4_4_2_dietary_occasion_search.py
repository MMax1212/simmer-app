"""Tests for US4.4.2: Backend Recipe Search Multi-Select Dietary, Occasion, and Time Filtering.

Mapped directly to acceptance criteria in docs/tasks/sprint-4/US4.4.2.md.
"""
from tests.conftest import auth_headers

BASE_RECIPE = {
    "title": "Base Dish",
    "description": "Standard recipe template for testing",
    "steps": [{"step_number": 1, "instruction": "Cook thoroughly and serve"}],
    "prep_time_mins": 10,
    "cook_time_mins": 15,
    "servings": 2,
    "ingredients": [
        {"name": "olive oil", "amount": 1, "unit": "tbsp"},
        {"name": "salt", "amount": 1, "unit": "pinch"},
    ],
}


def _create_recipe(client, headers, title, tags=None, cuisine=None, prep_time=10, cook_time=15, meal_type="dinner"):
    payload = {
        **BASE_RECIPE,
        "title": title,
        "tags": tags or [],
        "cuisine": cuisine,
        "prep_time_mins": prep_time,
        "cook_time_mins": cook_time,
        "meal_type": meal_type,
    }
    res = client.post("/api/v1/recipes", headers=headers, json=payload)
    assert res.status_code == 201, f"Failed to create recipe '{title}': {res.text}"
    return res.json()


def test_US4_4_2_criterion_1_dietary_single_filter(client):
    """US4.4.2 Criterion 1: Filtering by a single dietary tag returns only matching recipes."""
    h = auth_headers(client, email="chef1@example.com", username="chef1")
    _create_recipe(client, h, "Vegan Lentil Soup", tags=["#vegan"])
    _create_recipe(client, h, "Classic Beef Stew", tags=["#comfort-food"])

    res = client.get("/api/v1/recipes?dietary=vegan")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Vegan Lentil Soup" in titles
    assert "Classic Beef Stew" not in titles
    assert data["total"] == 1


def test_US4_4_2_criterion_2_dietary_multi_filter_intersection(client):
    """US4.4.2 Criterion 2: Multi-tag dietary queries enforce strict boolean AND intersection."""
    h = auth_headers(client, email="chef2@example.com", username="chef2")
    # Matches BOTH #vegan and #gluten-free
    _create_recipe(client, h, "Zucchini Noodles", tags=["#vegan", "#gluten-free"])
    # Matches #vegan ONLY
    _create_recipe(client, h, "Wheat Seitan Roast", tags=["#vegan"])
    # Matches #gluten-free ONLY
    _create_recipe(client, h, "Cheddar Omelette", tags=["#gluten-free", "#vegetarian"])

    res = client.get("/api/v1/recipes?dietary=vegan,gluten-free")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Zucchini Noodles" in titles
    assert "Wheat Seitan Roast" not in titles
    assert "Cheddar Omelette" not in titles
    assert data["total"] == 1


def test_US4_4_2_criterion_3_occasion_filter(client):
    """US4.4.2 Criterion 3: Filtering by an occasion tag returns matching recipes."""
    h = auth_headers(client, email="chef3@example.com", username="chef3")
    _create_recipe(client, h, "Quick Sheet-Pan Fajitas", tags=["#quick-dinner"])
    _create_recipe(client, h, "Slow-Braised Short Ribs", tags=["#date-night"])

    res = client.get("/api/v1/recipes?occasion=quick-dinner")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Quick Sheet-Pan Fajitas" in titles
    assert "Slow-Braised Short Ribs" not in titles
    assert data["total"] == 1


def test_US4_4_2_criterion_4_max_time_filter(client):
    """US4.4.2 Criterion 4: max_time parameter filters by prep_time_mins + cook_time_mins."""
    h = auth_headers(client, email="chef4@example.com", username="chef4")
    # 10 + 10 = 20 mins (<= 30)
    _create_recipe(client, h, "Express Salad", prep_time=10, cook_time=10)
    # 15 + 15 = 30 mins (<= 30 exact boundary)
    _create_recipe(client, h, "30-Min Stir Fry", prep_time=15, cook_time=15)
    # 15 + 25 = 40 mins (> 30 excluded)
    _create_recipe(client, h, "Slow Roast Chicken", prep_time=15, cook_time=25)

    res = client.get("/api/v1/recipes?max_time=30")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Express Salad" in titles
    assert "30-Min Stir Fry" in titles
    assert "Slow Roast Chicken" not in titles
    assert data["total"] == 2


def test_US4_4_2_criterion_5_combined_multi_facet_query(client):
    """US4.4.2 Criterion 5: Combined dietary, occasion, and max_time constraints enforce all filters."""
    h = auth_headers(client, email="chef5@example.com", username="chef5")
    # Matches dietary=vegan AND occasion=quick-dinner AND time <= 30
    _create_recipe(
        client, h, "Fast Vegan Stir Fry",
        tags=["#vegan", "#quick-dinner"], prep_time=10, cook_time=15
    )
    # Vegan & quick-dinner, but time = 45 mins (> 30 excluded)
    _create_recipe(
        client, h, "Slow Vegan Stew",
        tags=["#vegan", "#quick-dinner"], prep_time=15, cook_time=30
    )
    # Quick-dinner and time <= 30, but NOT vegan (excluded)
    _create_recipe(
        client, h, "Quick Turkey Wrap",
        tags=["#quick-dinner"], prep_time=10, cook_time=10
    )

    res = client.get("/api/v1/recipes?dietary=vegan&occasion=quick-dinner&max_time=30")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert titles == ["Fast Vegan Stir Fry"]
    assert data["total"] == 1


def test_US4_4_2_criterion_5_combined_with_cuisine_and_food_types(client):
    """US4.4.2 Criterion 5: Combining dietary tags with cuisine food types (e.g. Mexican + vegan)."""
    h = auth_headers(client, email="chef6@example.com", username="chef6")
    # Mexican + Vegan
    _create_recipe(
        client, h, "Vegan Black Bean Tacos",
        cuisine="Mexican", tags=["#vegan", "#gluten-free"], prep_time=10, cook_time=10
    )
    # Mexican but NOT Vegan
    _create_recipe(
        client, h, "Pork Carnitas Tacos",
        cuisine="Mexican", tags=["#gluten-free"], prep_time=15, cook_time=45
    )
    # Vegan but Italian (NOT Mexican)
    _create_recipe(
        client, h, "Vegan Penne All'Arrabbiata",
        cuisine="Italian", tags=["#vegan"], prep_time=10, cook_time=15
    )

    res = client.get("/api/v1/recipes?cuisine=Mexican&dietary=vegan")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Vegan Black Bean Tacos" in titles
    assert "Pork Carnitas Tacos" not in titles
    assert "Vegan Penne All'Arrabbiata" not in titles
    assert data["total"] == 1


def test_US4_4_2_criterion_6_zero_matches_empty_list(client):
    """US4.4.2 Criterion 6: Searches yielding zero results return HTTP 200 with total: 0 and empty items."""
    res = client.get("/api/v1/recipes?dietary=nonexistentdietaryflag")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_US4_4_2_edge_case_duplicate_and_messy_tags(client):
    """Edge Case: Tolerates extra commas, leading hashes, uppercase, and duplicate tags gracefully."""
    h = auth_headers(client, email="chef7@example.com", username="chef7")
    _create_recipe(client, h, "Clean Tofu Bowl", tags=["#vegan", "#nut-free"])

    # Pass duplicates, spaces, leading hash, and uppercase
    res = client.get("/api/v1/recipes?dietary=vegan, #VEGAN, , nut-free,")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert "Clean Tofu Bowl" in titles
    assert data["total"] == 1


def test_US4_4_2_edge_case_no_duplicate_rows_in_total_count(client):
    """Edge Case: Joining multiple matching tags does not multiply the recipe row or inflate total count."""
    h = auth_headers(client, email="chef8@example.com", username="chef8")
    _create_recipe(
        client, h, "Super Tagged Bowl",
        tags=["#vegan", "#vegetarian", "#gluten-free", "#nut-free", "#dairy-free"]
    )

    # Query matching multiple tags on the same recipe
    res = client.get("/api/v1/recipes?dietary=vegan,gluten-free,nut-free")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Super Tagged Bowl"


def test_US4_4_2_edge_case_all_filters_combined(client):
    """Edge Case: Full combination of keyword, cuisine, meal_type, difficulty, dietary, occasion, and max_time."""
    h = auth_headers(client, email="chef9@example.com", username="chef9")
    _create_recipe(
        client, h, "Ultimate Vegan Tacos",
        cuisine="Mexican", tags=["#vegan", "#quick-dinner"],
        prep_time=10, cook_time=10, meal_type="dinner"
    )
    _create_recipe(
        client, h, "Quick Vegan Burrito",
        cuisine="Mexican", tags=["#vegan", "#quick-dinner"],
        prep_time=15, cook_time=25, meal_type="dinner"  # 40 mins total > 25
    )

    res = client.get(
        "/api/v1/recipes?q=Tacos&cuisine=Mexican&meal_type=dinner&difficulty=medium"
        "&dietary=vegan&occasion=quick-dinner&max_time=25"
    )
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["items"]]
    assert titles == ["Ultimate Vegan Tacos"]
    assert data["total"] == 1


def test_US4_4_2_edge_case_legacy_tag_backward_compatibility(client):
    """Edge Case: Ensures existing ?tag= parameter from Sprint 2 continues functioning seamlessly."""
    h = auth_headers(client, email="chef10@example.com", username="chef10")
    _create_recipe(client, h, "Legacy Tagged Dish", tags=["#comfort-food"])

    res = client.get("/api/v1/recipes?tag=comfort-food")
    assert res.status_code == 200
    titles = [r["title"] for r in res.json()["items"]]
    assert "Legacy Tagged Dish" in titles
