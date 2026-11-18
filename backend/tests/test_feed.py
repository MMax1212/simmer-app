from datetime import datetime, timezone
import pytest

from app.models import Post, Recipe, User
from app.models.user_follow import UserFollow
from tests.conftest import auth_headers


def _create_post(db, author_id: int, caption: str, image_url: str = "https://example.com/food.jpg") -> Post:
    post = Post(
        author_id=author_id,
        caption=caption,
        image_url=image_url,
        media_type="image",
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


# --- US3.5 Task 3.5.3: Timeline Feed Endpoint Tests ---

def test_following_feed_requires_auth(client):
    """Verify HTTP 401 when accessing following feed without authentication."""
    res = client.get("/api/v1/feed?mode=following")
    assert res.status_code == 401


def test_following_feed_empty_when_not_following(client):
    """Verify empty feed is returned when the user does not follow anyone."""
    alice_h = auth_headers(client, email="feed_alone@example.com", username="feed_alone")
    res = client.get("/api/v1/feed?mode=following", headers=alice_h)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_following_feed_filters_by_followed_users(client, db_session):
    """Verify feed strictly returns posts authored by followed users and excludes unfollowed users."""
    alice_h = auth_headers(client, email="alice_feed@example.com", username="alice_feed")
    bob_h = auth_headers(client, email="bob_feed@example.com", username="bob_feed")
    charlie_h = auth_headers(client, email="charlie_feed@example.com", username="charlie_feed")

    alice_id = client.get("/api/v1/users/alice_feed").json()["id"]
    bob_id = client.get("/api/v1/users/bob_feed").json()["id"]
    charlie_id = client.get("/api/v1/users/charlie_feed").json()["id"]

    # Alice follows Bob only
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)

    # Bob creates a post
    post_bob = _create_post(db_session, author_id=bob_id, caption="Bob's Homemade Pizza")
    # Charlie creates a post
    post_charlie = _create_post(db_session, author_id=charlie_id, caption="Charlie's Tacos")

    # Alice requests her following feed
    res = client.get("/api/v1/feed?mode=following", headers=alice_h)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == post_bob.id
    assert data["items"][0]["caption"] == "Bob's Homemade Pizza"
    assert data["items"][0]["author"]["username"] == "bob_feed"


def test_following_feed_chronological_order(client, db_session):
    """Verify posts in the feed are delivered in reverse chronological order (newest first)."""
    alice_h = auth_headers(client, email="alice_chrono@example.com", username="alice_chrono")
    bob_h = auth_headers(client, email="bob_chrono@example.com", username="bob_chrono")

    bob_id = client.get("/api/v1/users/bob_chrono").json()["id"]
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)

    post1 = _create_post(db_session, author_id=bob_id, caption="First Post")
    post2 = _create_post(db_session, author_id=bob_id, caption="Second Post")

    res = client.get("/api/v1/feed?mode=following", headers=alice_h)
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 2
    # Newest first
    assert items[0]["id"] == post2.id
    assert items[1]["id"] == post1.id


def test_following_feed_pagination(client, db_session):
    """Verify pagination limit and offset parameters on following feed."""
    alice_h = auth_headers(client, email="alice_page@example.com", username="alice_page")
    bob_h = auth_headers(client, email="bob_page@example.com", username="bob_page")

    bob_id = client.get("/api/v1/users/bob_page").json()["id"]
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)

    for i in range(3):
        _create_post(db_session, author_id=bob_id, caption=f"Post {i}")

    # Page 1: limit=2, offset=0
    res1 = client.get("/api/v1/feed?mode=following&limit=2&offset=0", headers=alice_h)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] == 3
    assert len(data1["items"]) == 2
    assert data1["limit"] == 2
    assert data1["offset"] == 0

    # Page 2: limit=2, offset=2
    res2 = client.get("/api/v1/feed?mode=following&limit=2&offset=2", headers=alice_h)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total"] == 3
    assert len(data2["items"]) == 1
    assert data2["offset"] == 2


def test_global_community_feed_accessible_publicly(client, db_session):
    """Verify global community feed is accessible publicly without authentication."""
    bob_h = auth_headers(client, email="bob_public@example.com", username="bob_public")
    bob_id = client.get("/api/v1/users/bob_public").json()["id"]

    post = _create_post(db_session, author_id=bob_id, caption="Public Carbonara")

    # Unauthenticated request with mode=global
    res = client.get("/api/v1/feed?mode=global")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    found = any(item["id"] == post.id for item in data["items"])
    assert found is True


# --- US3.5 Task 3.5.6: Automated Integration Tests for Follow Integrity & Filtering ---

def test_multi_user_follow_network_feed_isolation_and_unfollow(client, db_session):
    """Verify multi-hop follower network isolation and immediate feed updates on unfollow."""
    alice_h = auth_headers(client, email="alice_net@example.com", username="alice_net")
    bob_h = auth_headers(client, email="bob_net@example.com", username="bob_net")
    charlie_h = auth_headers(client, email="charlie_net@example.com", username="charlie_net")
    dan_h = auth_headers(client, email="dan_net@example.com", username="dan_net")

    alice_id = client.get("/api/v1/users/alice_net").json()["id"]
    bob_id = client.get("/api/v1/users/bob_net").json()["id"]
    charlie_id = client.get("/api/v1/users/charlie_net").json()["id"]
    dan_id = client.get("/api/v1/users/dan_net").json()["id"]

    # Alice follows Bob and Charlie
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    client.post(f"/api/v1/users/{charlie_id}/follow", headers=alice_h)

    # Bob follows Charlie
    client.post(f"/api/v1/users/{charlie_id}/follow", headers=bob_h)

    # Charlie and Dan follow nobody

    # Everyone except Alice creates a post
    post_bob = _create_post(db_session, author_id=bob_id, caption="Bob's Risotto")
    post_charlie = _create_post(db_session, author_id=charlie_id, caption="Charlie's Gnocchi")
    post_dan = _create_post(db_session, author_id=dan_id, caption="Dan's Paella")

    # 1. Check Alice's feed: should contain Bob's and Charlie's posts (2 items), NOT Dan's
    alice_feed = client.get("/api/v1/feed?mode=following", headers=alice_h).json()
    alice_post_ids = [item["id"] for item in alice_feed["items"]]
    assert alice_feed["total"] == 2
    assert post_bob.id in alice_post_ids
    assert post_charlie.id in alice_post_ids
    assert post_dan.id not in alice_post_ids

    # 2. Check Bob's feed: should contain ONLY Charlie's post (1 item)
    bob_feed = client.get("/api/v1/feed?mode=following", headers=bob_h).json()
    assert bob_feed["total"] == 1
    assert bob_feed["items"][0]["id"] == post_charlie.id

    # 3. Check Charlie's feed: follows nobody -> 0 items
    charlie_feed = client.get("/api/v1/feed?mode=following", headers=charlie_h).json()
    assert charlie_feed["total"] == 0
    assert charlie_feed["items"] == []

    # 4. Alice unfollows Bob
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)

    # Alice's feed immediately updates: now contains ONLY Charlie's post
    alice_updated = client.get("/api/v1/feed?mode=following", headers=alice_h).json()
    assert alice_updated["total"] == 1
    assert alice_updated["items"][0]["id"] == post_charlie.id


def test_feed_linked_recipe_payload(client, db_session):
    """Verify posts linked to recipes include full recipe summary payload in feed."""
    alice_h = auth_headers(client, email="alice_rec@example.com", username="alice_rec")
    bob_h = auth_headers(client, email="bob_rec@example.com", username="bob_rec")
    bob_id = client.get("/api/v1/users/bob_rec").json()["id"]

    # Bob creates a recipe
    recipe = Recipe(
        author_id=bob_id,
        title="Homemade Lasagna",
        description="Classic beef lasagna",
        cuisine="Italian",
        meal_type="dinner",
        difficulty="medium",
        prep_time_mins=30,
        cook_time_mins=60,
        servings=6,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    # Bob creates a post linked to this recipe
    post = Post(
        author_id=bob_id,
        caption="Just pulled this lasagna out of the oven!",
        image_url="https://example.com/lasagna.jpg",
        media_type="image",
        recipe_id=recipe.id,
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    # Alice follows Bob and retrieves feed
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    feed = client.get("/api/v1/feed?mode=following", headers=alice_h).json()

    assert feed["total"] == 1
    item = feed["items"][0]
    assert item["id"] == post.id
    assert item["recipe"] is not None
    assert item["recipe"]["id"] == recipe.id
    assert item["recipe"]["title"] == "Homemade Lasagna"
    assert item["recipe"]["cook_time_mins"] == 60
    assert item["recipe"]["difficulty"] == "medium"

