"""Discovery integration: real HTTP writes, stored data, ranking SQL and public DTOs.

Older suites isolate query mathematics and card rendering. These cases bridge those
boundaries without mocking ranking/matching services. Only the discovery clock is
injected; every test uses the existing disposable in-memory database fixture.
"""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.discovery import get_discovery_clock
from app.main import app
from app.models import Post, Recipe, User
from tests.conftest import auth_headers

# Capture one clock ahead of HTTP writes without patching every route's datetime.
# Relative recipe ages stay deterministic, without a calendar date that can expire.
NOW = datetime.now(timezone.utc) + timedelta(days=1)
RECIPES_URL = "/api/v1/recipes"
POSTS_URL = "/api/v1/posts"
PROFILE_URL = "/api/v1/users/me"


@pytest.fixture()
def discovery_case(client: TestClient, db_session: Session, monkeypatch) -> dict:
    """Seed known ages once; use HTTP for engagement and saved profile changes."""
    monkeypatch.setitem(app.dependency_overrides, get_discovery_clock, lambda: NOW)
    headers = auth_headers(client)
    user = db_session.query(User).filter_by(username="ana").one()
    fresh = Recipe(author_id=user.id, title="Fresh Italian", cuisine="Italian",
                   created_at=NOW - timedelta(hours=2))
    older = Recipe(author_id=user.id, title="Older Italian", cuisine="Italian",
                   created_at=NOW - timedelta(hours=24))
    quiet = Recipe(author_id=user.id, title="Quiet Mexican", cuisine="Mexican",
                   created_at=NOW - timedelta(hours=1))
    db_session.add_all([fresh, older, quiet])
    db_session.flush()
    posts = [Post(author_id=user.id, recipe_id=recipe.id, caption="Dinner",
                  image_url="/test.jpg") for recipe in [fresh, fresh, older]]
    db_session.add_all(posts)
    db_session.commit()
    response = client.put(PROFILE_URL, headers=headers,
                          json={"culinary_preferences": ["Italian"]})
    assert response.status_code == status.HTTP_200_OK
    return {"headers": headers, "fresh": fresh.id, "older": older.id,
            "quiet": quiet.id, "posts": [post.id for post in posts]}


def read_cards(client: TestClient, endpoint: str, headers: dict) -> list[dict]:
    """Fail on HTTP/shape errors before inspecting scores to avoid false positives."""
    response = client.get(f"{RECIPES_URL}/{endpoint}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()
    assert isinstance(cards, list)
    return cards


# All three write paths must feed the same score. Two posts and two comments make
# accidental joins/count multiplication observable; the expected value comes from
# the written specification, not constants imported from the implementation.
@pytest.mark.parametrize("endpoint", ["trending", "recommended"])
def test_http_engagement_writes_feed_exact_gravity_scores(
    client: TestClient, discovery_case: dict, endpoint: str,
) -> None:
    case = discovery_case
    headers = case["headers"]
    first, second, old_post = case["posts"]
    for post in [first, second, old_post]:
        response = client.post(f"{POSTS_URL}/{post}/like", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    for content in ["First comment", "Second comment"]:
        response = client.post(f"{POSTS_URL}/{first}/comments", headers=headers,
                               json={"content": content})
        assert response.status_code == status.HTTP_201_CREATED
    response = client.post(f"{RECIPES_URL}/{case['fresh']}/complete", headers=headers,
                           json={"rating": 5})
    assert response.status_code == status.HTTP_201_CREATED
    cards = read_cards(client, endpoint, headers)
    assert [card["id"] for card in cards] == [case["fresh"], case["older"]]
    assert cards[0]["trending_score"] == pytest.approx((2 * 2 + 2 * 3 + 5) / 4 ** 1.5)
    assert cards[0]["likes_count"] == 2 and cards[0]["completed_count"] == 1
    assert cards[1]["trending_score"] == pytest.approx(2 / 26 ** 1.5)
    # Unliking is a deletion, not a new event: discovery must reflect persisted state.
    response = client.post(f"{POSTS_URL}/{second}/like", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    updated = read_cards(client, endpoint, headers)[0]
    assert updated["likes_count"] == 1
    assert updated["trending_score"] == pytest.approx((2 + 2 * 3 + 5) / 4 ** 1.5)


# A score-only unit test cannot detect a route that drops its clock dependency,
# caches stale ordering, or paginates before ranking. These scores deliberately cross
# as both recipes age, so unchanged ordering cannot accidentally pass this scenario.
@pytest.mark.parametrize("endpoint", ["trending", "recommended"])
def test_api_clock_advance_decays_scores_and_changes_first_page(
    client: TestClient, discovery_case: dict, monkeypatch, endpoint: str,
) -> None:
    case = discovery_case
    headers = case["headers"]
    response = client.post(f"{POSTS_URL}/{case['posts'][0]}/like", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # Two real cooks avoid the logging endpoint's same-user cooldown rule.
    other = auth_headers(client, email="second@example.com", username="second")
    for cook in [headers, other]:
        response = client.post(f"{RECIPES_URL}/{case['older']}/complete", headers=cook, json={})
        assert response.status_code == status.HTTP_201_CREATED
    before = read_cards(client, endpoint, headers)
    assert [card["id"] for card in before] == [case["fresh"], case["older"]]
    assert [card["trending_score"] for card in before] == pytest.approx(
        [2 / 4 ** 1.5, 10 / 26 ** 1.5]
    )
    monkeypatch.setitem(app.dependency_overrides, get_discovery_clock,
                        lambda: NOW + timedelta(hours=24))
    after = read_cards(client, endpoint, headers)
    assert [card["id"] for card in after] == [case["older"], case["fresh"]]
    assert [card["trending_score"] for card in after] == pytest.approx(
        [10 / 50 ** 1.5, 2 / 28 ** 1.5]
    )
    response = client.get(f"{RECIPES_URL}/{endpoint}?limit=1", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert [card["id"] for card in response.json()] == [case["older"]]


# Saving through the profile API exercises normalization, persistence and session
# selection together. A second real account guards against shared/cached preferences.
def test_saved_profile_edits_change_matches_without_changing_other_accounts(
    client: TestClient, discovery_case: dict,
) -> None:
    case = discovery_case
    headers = case["headers"]
    other = auth_headers(client, email="other@example.com", username="other")
    response = client.put(PROFILE_URL, headers=other,
                          json={"culinary_preferences": ["Italian"]})
    assert response.status_code == status.HTTP_200_OK
    response = client.put(PROFILE_URL, headers=headers,
                          json={"culinary_preferences": [" Mexican "]})
    assert response.status_code == status.HTTP_200_OK
    assert [card["id"] for card in read_cards(client, "recommended", headers)] == [case["quiet"]]
    assert {card["id"] for card in read_cards(client, "recommended", other)} == {
        case["fresh"], case["older"],
    }
    response = client.get(f"{RECIPES_URL}/recommended?preferences=Italian", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert [card["id"] for card in response.json()] == [case["quiet"]]
    response = client.put(PROFILE_URL, headers=headers,
                          json={"culinary_preferences": ["No matching cuisine"]})
    assert response.status_code == status.HTTP_200_OK
    assert read_cards(client, "recommended", headers) == []
