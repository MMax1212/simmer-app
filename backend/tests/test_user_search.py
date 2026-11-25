import pytest
from app.core.security import hash_password
from app.models import User, UserFollow
from tests.conftest import auth_headers


def _create_user(db, email: str, username: str, is_active: bool = True) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password("password123"),
        role="user",
        is_active=is_active,
        bio=f"Bio for {username}",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- US4.1 Task 4.1.1 & 4.1.2: User Search Endpoint Tests ---

def test_user_search_case_insensitive_prefix_matching(client, db_session):
    """Verify search returns matching active users using case-insensitive prefix matching."""
    _create_user(db_session, "mario_chef@example.com", "mario_chef")
    _create_user(db_session, "mario_bakes@example.com", "mario_bakes")
    _create_user(db_session, "maria_cooks@example.com", "maria_cooks")
    _create_user(db_session, "luigi_chef@example.com", "luigi_chef")

    # 1. Prefix 'mario' matches mario_bakes and mario_chef in alphabetical order
    res = client.get("/api/v1/users/search?q=mario")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    usernames = [u["username"] for u in data["items"]]
    assert usernames == ["mario_bakes", "mario_chef"]

    # 2. Case-insensitive matching ('MARIO')
    res_upper = client.get("/api/v1/users/search?q=MARIO")
    assert res_upper.status_code == 200
    assert [u["username"] for u in res_upper.json()["items"]] == ["mario_bakes", "mario_chef"]

    # 3. Broader prefix 'mari' matches maria_cooks, mario_bakes, mario_chef
    res_broad = client.get("/api/v1/users/search?q=mari")
    assert res_broad.status_code == 200
    assert res_broad.json()["total"] == 3
    assert [u["username"] for u in res_broad.json()["items"]] == [
        "maria_cooks",
        "mario_bakes",
        "mario_chef",
    ]


def test_user_search_excludes_deactivated_users(client, db_session):
    """Verify deactivated accounts are excluded from search results."""
    _create_user(db_session, "active_alex@example.com", "active_alex", is_active=True)
    _create_user(db_session, "banned_alex@example.com", "banned_alex", is_active=False)

    res = client.get("/api/v1/users/search?q=banned_alex")
    assert res.status_code == 200
    assert res.json()["total"] == 0
    assert res.json()["items"] == []


def test_user_search_self_exclusion_when_authenticated(client, db_session):
    """Verify authenticated user is excluded from their own search results."""
    alice_h = auth_headers(client, email="alice_searcher@example.com", username="alice_searcher")
    _create_user(db_session, "alice_baker@example.com", "alice_baker")

    # When Alice searches 'alice' authenticated, she sees alice_baker but NOT herself
    res_auth = client.get("/api/v1/users/search?q=alice", headers=alice_h)
    assert res_auth.status_code == 200
    usernames = [u["username"] for u in res_auth.json()["items"]]
    assert "alice_baker" in usernames
    assert "alice_searcher" not in usernames

    # When searched unauthenticated, both are returned
    res_anon = client.get("/api/v1/users/search?q=alice")
    assert res_anon.status_code == 200
    anon_usernames = [u["username"] for u in res_anon.json()["items"]]
    assert "alice_baker" in anon_usernames
    assert "alice_searcher" in anon_usernames


def test_user_search_pagination(client, db_session):
    """Verify pagination limit and offset parameters on search results."""
    for i in range(5):
        _create_user(db_session, f"paged_{i}@example.com", f"paged_user_{i}")

    # Page 1: limit=2, offset=0
    res1 = client.get("/api/v1/users/search?q=paged_user&limit=2&offset=0")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] == 5
    assert len(data1["items"]) == 2
    assert data1["limit"] == 2
    assert data1["offset"] == 0
    assert data1["items"][0]["username"] == "paged_user_0"
    assert data1["items"][1]["username"] == "paged_user_1"

    # Page 2: limit=2, offset=2
    res2 = client.get("/api/v1/users/search?q=paged_user&limit=2&offset=2")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total"] == 5
    assert len(data2["items"]) == 2
    assert data2["items"][0]["username"] == "paged_user_2"
    assert data2["items"][1]["username"] == "paged_user_3"


def test_user_search_empty_query_returns_active_users(client, db_session):
    """Verify empty query string returns all active users paginated."""
    _create_user(db_session, "user_alpha@example.com", "user_alpha")
    _create_user(db_session, "user_beta@example.com", "user_beta")

    res = client.get("/api/v1/users/search?q=")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2
    usernames = [u["username"] for u in data["items"]]
    assert "user_alpha" in usernames
    assert "user_beta" in usernames


def test_user_search_follow_status_and_follower_counts(client, db_session):
    """Verify results include accurate is_following state and follower counts."""
    alice_h = auth_headers(client, email="alice_net_search@example.com", username="alice_net_search")
    bob = _create_user(db_session, "bob_chef_search@example.com", "bob_chef_search")
    charlie = _create_user(db_session, "charlie_fan_search@example.com", "charlie_fan_search")

    alice_id = client.get("/api/v1/users/alice_net_search").json()["id"]

    # Charlie and Alice follow Bob
    db_session.add_all([
        UserFollow(follower_id=charlie.id, following_id=bob.id),
        UserFollow(follower_id=alice_id, following_id=bob.id),
    ])
    db_session.commit()

    # 1. Alice searches for Bob: is_following is True, followers_count is 2
    res_alice = client.get("/api/v1/users/search?q=bob_chef", headers=alice_h)
    assert res_alice.status_code == 200
    bob_item = res_alice.json()["items"][0]
    assert bob_item["username"] == "bob_chef_search"
    assert bob_item["is_following"] is True
    assert bob_item["followers_count"] == 2

    # 2. Anonymous visitor searches for Bob: is_following is False, followers_count is 2
    res_anon = client.get("/api/v1/users/search?q=bob_chef")
    assert res_anon.status_code == 200
    bob_anon = res_anon.json()["items"][0]
    assert bob_anon["username"] == "bob_chef_search"
    assert bob_anon["is_following"] is False
    assert bob_anon["followers_count"] == 2
