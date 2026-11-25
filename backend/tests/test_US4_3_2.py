"""Test-first contracts for public trending and private recipe recommendations."""
from datetime import datetime, timedelta, timezone

import pytest

from app.api.discovery import get_discovery_clock
from app.core.config import settings
from app.main import app
from app.models import CompletedRecipe, Post, PostLike, Recipe, Tag, User
from tests.conftest import auth_headers

NOW = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def discovery_policy(monkeypatch):
    """Freeze clock and policy so scores never depend on test-run time or .env."""
    monkeypatch.setitem(app.dependency_overrides, get_discovery_clock, lambda: NOW)
    for name, value in {
        "trending_like_weight": 3.0, "trending_comment_weight": 5.0,
        "trending_completion_weight": 4.0, "trending_window_days": 7,
        "trending_decay_hours": 24.0,
    }.items():
        monkeypatch.setattr(settings, name, value)


@pytest.fixture()
def discovery_data(client, db_session):
    headers = auth_headers(client)
    user = db_session.query(User).filter_by(username="ana").one()
    user.culinary_preferences = [" Italian ", "#VEGAN"]
    best = Recipe(author_id=user.id, title="Italian vegan", cuisine="Italian")
    best.tags = [Tag(name="#vegan"), Tag(name="#quick")]
    cuisine_only = Recipe(author_id=user.id, title="Italian pasta", cuisine="ITALIAN")
    unrelated = Recipe(author_id=user.id, title="Other recipe", cuisine="Mexican")
    db_session.add_all([best, cuisine_only, unrelated])
    db_session.flush()
    post = Post(author_id=user.id, recipe_id=best.id, caption="Dinner", image_url="/dish.jpg")
    db_session.add(post)
    db_session.flush()
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.add(CompletedRecipe(
        user_id=user.id, recipe_id=cuisine_only.id, cooked_at=NOW - timedelta(days=30),
    ))
    db_session.commit()
    return headers, user, best, cuisine_only, unrelated


def test_trending_is_public_ranked_and_returns_safe_summary(client, discovery_data):
    _, _, best, _, _ = discovery_data
    response = client.get("/api/v1/recipes/trending")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20 and data["offset"] == 0
    assert [item["id"] for item in data["items"]] == [best.id]
    item = data["items"][0]
    assert item["score"] > 0 and item["likes_count"] == 1
    assert item["author_username"] == "ana"
    assert item["tags"] == ["#vegan", "#quick"]
    assert "email" not in item and "hashed_password" not in item


@pytest.mark.parametrize("endpoint", ["trending", "recommended"])
@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
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
    assert data["personalized"] is True
    assert [item["id"] for item in data["items"]] == [best.id, cuisine_only.id]
    assert unrelated.id not in [item["id"] for item in data["items"]]
    assert len({item["id"] for item in data["items"]}) == 2


def test_profiles_are_isolated_and_empty_preferences_are_explicit(client, discovery_data):
    headers, user, _, _, unrelated = discovery_data
    other = auth_headers(client, email="other@example.com", username="other")
    response = client.get("/api/v1/recipes/recommended", headers=other)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["personalized"] is False
    assert client.get("/api/v1/recipes/recommended", headers=headers).json()["personalized"] is True
    # Caller-supplied preferences cannot impersonate another user's stored profile.
    response = client.get("/api/v1/recipes/recommended?preferences=Mexican", headers=headers)
    assert unrelated.id not in [item["id"] for item in response.json()["items"]]


def test_recommendation_pagination_and_no_match(client, db_session, discovery_data):
    headers, user, best, cuisine_only, _ = discovery_data
    response = client.get("/api/v1/recipes/recommended?limit=1&offset=1", headers=headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [cuisine_only.id]
    user.culinary_preferences = ["Does not exist"]
    db_session.commit()
    response = client.get("/api/v1/recipes/recommended", headers=headers)
    assert response.json()["items"] == [] and response.json()["personalized"] is True


def test_numeric_recipe_route_still_works(client, discovery_data):
    _, _, best, _, _ = discovery_data
    assert client.get(f"/api/v1/recipes/{best.id}").status_code == 200



def test_trending_pagination_uses_stable_rank_and_configured_weights(
    client, db_session, discovery_data, monkeypatch,
):
    _, user, best, _, unrelated = discovery_data
    post = Post(author_id=user.id, recipe_id=unrelated.id, caption="Other", image_url="/x.jpg")
    db_session.add(post)
    db_session.flush()
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.commit()
    monkeypatch.setattr(settings, "trending_like_weight", 6.0)
    first = client.get("/api/v1/recipes/trending?limit=1").json()
    second = client.get("/api/v1/recipes/trending?limit=1&offset=1").json()
    assert [item["id"] for item in first["items"]] == [best.id]
    assert first["items"][0]["score"] == pytest.approx(6.0)
    assert [item["id"] for item in second["items"]] == [unrelated.id]
    assert second["limit"] == 1 and second["offset"] == 1
    assert client.get("/api/v1/recipes/trending?offset=100").json()["items"] == []


def test_empty_trending_is_a_successful_page(client):
    response = client.get("/api/v1/recipes/trending")
    assert response.status_code == 200
    assert response.json() == {"limit": 20, "offset": 0, "items": []}


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


@pytest.mark.parametrize("preferences", [["# "], ["' OR 1=1 --"]])
def test_unusable_or_literal_preferences_do_not_broaden_matches(
    client, db_session, discovery_data, preferences,
):
    headers, user, *_ = discovery_data
    user.culinary_preferences = preferences
    db_session.commit()
    response = client.get("/api/v1/recipes/recommended", headers=headers)
    assert response.status_code == 200 and response.json()["items"] == []
