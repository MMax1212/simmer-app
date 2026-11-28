"""Test-first contracts for public trending and private recipe recommendations."""
from datetime import datetime, timedelta, timezone

import pytest

from app.api.discovery import get_discovery_clock
from app.main import app
from app.models import CompletedRecipe, Post, PostLike, Recipe, Tag, User
from tests.conftest import auth_headers

NOW = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def discovery_clock(monkeypatch):
    """Freeze the clock so recipe-age scores never depend on test-run time."""
    monkeypatch.setitem(app.dependency_overrides, get_discovery_clock, lambda: NOW)


@pytest.fixture()
def discovery_data(client, db_session):
    headers = auth_headers(client)
    user = db_session.query(User).filter_by(username="ana").one()
    user.culinary_preferences = [" Italian ", "#VEGAN"]
    best = Recipe(author_id=user.id, created_at=NOW, title="Italian vegan", cuisine="Italian")
    best.tags = [Tag(name="#vegan"), Tag(name="#quick")]
    cuisine_only = Recipe(
        author_id=user.id, created_at=NOW, title="Italian pasta", cuisine="ITALIAN",
    )
    unrelated = Recipe(author_id=user.id, created_at=NOW, title="Other recipe", cuisine="Mexican")
    db_session.add_all([best, cuisine_only, unrelated])
    db_session.flush()
    post = Post(author_id=user.id, recipe_id=best.id, caption="Dinner", image_url="/dish.jpg")
    db_session.add(post)
    db_session.flush()
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.add(CompletedRecipe(
        user_id=user.id, recipe_id=cuisine_only.id, cooked_at=NOW, rating=5,
    ))
    db_session.commit()
    return headers, user, best, cuisine_only, unrelated


def test_trending_is_public_ranked_and_returns_safe_summary(client, discovery_data):
    _, _, best, cuisine_only, _ = discovery_data
    response = client.get("/api/v1/recipes/trending")
    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == [cuisine_only.id, best.id]
    item = data[1]
    assert item["trending_score"] > 0 and item["likes_count"] == 1
    assert item["author_username"] == "ana"
    assert item["completed_count"] == 0
    assert "email" not in item and "hashed_password" not in item


@pytest.mark.parametrize("endpoint", ["trending", "recommended"])
@pytest.mark.parametrize("query", ["limit=0", "limit=21", "offset=-1"])
def test_discovery_rejects_invalid_pagination(client, discovery_data, endpoint, query):
    headers, *_ = discovery_data
    response = client.get(f"/api/v1/recipes/{endpoint}?{query}", headers=headers)
    assert response.status_code == 422
    # A 422 from the old /{recipe_id} route is not pagination validation.
    parameter = query.split("=")[0]
    assert ["query", parameter] in [error["loc"] for error in response.json()["detail"]]


def test_recommendations_require_authentication(client):
    response = client.get("/api/v1/recipes/recommended")
    assert response.status_code == 401


def test_recommendations_use_current_users_preferences_and_match_count(client, discovery_data):
    headers, _, best, cuisine_only, unrelated = discovery_data
    response = client.get("/api/v1/recipes/recommended", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == [best.id, cuisine_only.id]
    assert unrelated.id not in [item["id"] for item in data]
    assert len({item["id"] for item in data}) == 2


def test_empty_preferences_fall_back_to_top_rated_without_leaking_profile(client, discovery_data):
    headers, _, best, cuisine_only, unrelated = discovery_data
    other = auth_headers(client, email="other@example.com", username="other")
    response = client.get("/api/v1/recipes/recommended", headers=other)
    assert response.status_code == 200
    assert response.json()[0]["id"] == cuisine_only.id
    # Caller-supplied preferences cannot impersonate another user's stored profile.
    response = client.get("/api/v1/recipes/recommended?preferences=Mexican", headers=headers)
    assert unrelated.id not in [item["id"] for item in response.json()]


def test_recommendation_pagination_and_no_match(client, db_session, discovery_data):
    headers, user, best, cuisine_only, _ = discovery_data
    response = client.get("/api/v1/recipes/recommended?limit=1&offset=1", headers=headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [cuisine_only.id]
    user.culinary_preferences = ["Does not exist"]
    db_session.commit()
    response = client.get("/api/v1/recipes/recommended", headers=headers)
    assert response.json() == []


def test_numeric_recipe_route_still_works(client, discovery_data):
    _, _, best, cuisine_only, _ = discovery_data
    assert client.get(f"/api/v1/recipes/{best.id}").status_code == 200


def test_trending_pagination_uses_gravity_ranking(client, discovery_data):
    _, _, best, cuisine_only, _ = discovery_data
    first = client.get("/api/v1/recipes/trending?limit=1").json()
    second = client.get("/api/v1/recipes/trending?limit=1&offset=1").json()
    assert first[0]["id"] == cuisine_only.id
    assert first[0]["trending_score"] == pytest.approx(5 / 2 ** 1.5)
    assert second[0]["id"] == best.id
    assert client.get("/api/v1/recipes/trending?offset=100").json() == []


def test_empty_trending_is_a_successful_list(client):
    response = client.get("/api/v1/recipes/trending")
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_or_inactive_sessions_cannot_read_recommendations(
    client, db_session, discovery_data,
):
    headers, user, *_ = discovery_data
    assert client.get("/api/v1/recipes/recommended", headers={
        "Authorization": "Bearer invalid",
    }).status_code == 401
    user.is_active = False
    db_session.commit()
    assert client.get("/api/v1/recipes/recommended", headers=headers).status_code == 401


@pytest.mark.parametrize("preferences", [["' OR 1=1 --"]])
def test_unusable_or_literal_preferences_do_not_broaden_matches(
    client, db_session, discovery_data, preferences,
):
    headers, user, *_ = discovery_data
    user.culinary_preferences = preferences
    db_session.commit()
    response = client.get("/api/v1/recipes/recommended", headers=headers)
    assert response.status_code == 200 and response.json() == []


def test_default_and_maximum_page_sizes_and_newest_cold_start(client, db_session):
    headers = auth_headers(client)
    user = db_session.query(User).filter_by(username="ana").one()
    # No ratings or engagement: newest recipes form a deterministic cold-start list.
    recipes = [Recipe(author_id=user.id, title=f"Recipe {i}",
                      created_at=NOW - timedelta(hours=i)) for i in range(25)]
    db_session.add_all(recipes)
    db_session.commit()
    for endpoint in ["trending", "recommended"]:
        response = client.get(f"/api/v1/recipes/{endpoint}", headers=headers)
        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [r.id for r in recipes[:10]]
        assert len(client.get(f"/api/v1/recipes/{endpoint}?limit=20", headers=headers).json()) == 20
        page = client.get(f"/api/v1/recipes/{endpoint}?limit=5&offset=10", headers=headers)
        assert [item["id"] for item in page.json()] == [r.id for r in recipes[10:15]]
        assert response.json()[0]["trending_score"] == 0
        assert response.json()[0]["completed_count"] == 0


def test_unusable_preferences_use_fallback_but_real_nonmatches_stay_empty(
    client, db_session, discovery_data,
):
    headers, user, _, cuisine_only, _ = discovery_data
    user.culinary_preferences = ["# "]
    db_session.commit()
    response = client.get("/api/v1/recipes/recommended", headers=headers)
    assert response.json()[0]["id"] == cuisine_only.id


def test_fallback_orders_average_rating_then_newest_and_excludes_future(
    client, db_session, discovery_data,
):
    _, user, best, cuisine_only, unrelated = discovery_data
    user.culinary_preferences = []
    best.created_at = NOW - timedelta(days=1)
    db_session.add_all([
        CompletedRecipe(user_id=user.id, recipe_id=best.id, cooked_at=NOW, rating=5),
        CompletedRecipe(user_id=user.id, recipe_id=unrelated.id, cooked_at=NOW, rating=1),
        CompletedRecipe(user_id=user.id, recipe_id=unrelated.id, cooked_at=NOW, rating=5),
        Recipe(author_id=user.id, title="Future", created_at=NOW + timedelta(hours=1)),
    ])
    db_session.commit()
    headers = auth_headers(client, email="cold@example.com", username="cold")
    items = client.get("/api/v1/recipes/recommended", headers=headers).json()
    assert [item["id"] for item in items] == [cuisine_only.id, best.id, unrelated.id]
    assert all(set(item) == {"id", "title", "image_url", "cuisine", "difficulty",
                            "cook_time_mins", "author_username", "trending_score",
                            "likes_count", "completed_count"} for item in items)


def test_future_ratings_do_not_change_fallback_or_return_future_metrics(
    client, db_session, discovery_data,
):
    headers, user, _, cuisine_only, unrelated = discovery_data
    user.culinary_preferences = []
    db_session.add(CompletedRecipe(
        user_id=user.id, recipe_id=unrelated.id,
        cooked_at=NOW + timedelta(seconds=1), rating=5,
    ))
    db_session.commit()
    items = client.get("/api/v1/recipes/recommended", headers=headers).json()
    assert items[0]["id"] == cuisine_only.id
    unrelated_card = next(item for item in items if item["id"] == unrelated.id)
    assert unrelated_card["completed_count"] == 0
    assert unrelated_card["trending_score"] == 0
    # Both endpoints share counts and the formula, even with different ordering.
    trending = client.get("/api/v1/recipes/trending").json()
    assert items[0] == trending[0]


def test_meal_type_and_normalized_tags_match_without_duplicate_cards(
    client, db_session, discovery_data,
):
    headers, user, best, _, unrelated = discovery_data
    user.culinary_preferences = [" Quick Dinner ", "# Vegan "]
    unrelated.meal_type = "quick-dinner"
    # Equivalent stored spellings count once rather than inflating preference relevance.
    best.tags.append(Tag(name="vegan"))
    db_session.commit()
    items = client.get("/api/v1/recipes/recommended", headers=headers).json()
    assert [item["id"] for item in items] == [best.id, unrelated.id]
    assert len({item["id"] for item in items}) == 2
