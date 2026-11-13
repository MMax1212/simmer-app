import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.models import User
from app.models.user_follow import UserFollow
from tests.conftest import auth_headers


def _create_user(db, email: str, username: str) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password("password123"),
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- US3.5 Task 3.5.1: Create Follow Relationship Model & Constraints ---

def test_user_can_follow_another_user(db_session):
    """Verify that User A can follow User B and the relationship persists."""
    alice = _create_user(db_session, "alice@example.com", "alice")
    bob = _create_user(db_session, "bob@example.com", "bob")

    follow = UserFollow(follower_id=alice.id, following_id=bob.id)
    db_session.add(follow)
    db_session.commit()

    saved = db_session.scalar(
        select(UserFollow).where(
            UserFollow.follower_id == alice.id,
            UserFollow.following_id == bob.id,
        )
    )
    assert saved is not None
    assert saved.follower_id == alice.id
    assert saved.following_id == bob.id
    assert saved.created_at is not None


def test_cannot_follow_same_user_twice(db_session):
    """Verify that duplicate follow records are rejected by the primary key/unique constraint."""
    alice = _create_user(db_session, "alice_dup@example.com", "alice_dup")
    bob = _create_user(db_session, "bob_dup@example.com", "bob_dup")

    follow1 = UserFollow(follower_id=alice.id, following_id=bob.id)
    db_session.add(follow1)
    db_session.commit()

    follow2 = UserFollow(follower_id=alice.id, following_id=bob.id)
    db_session.add(follow2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cannot_follow_self(db_session):
    """Verify database check constraint prevents a user from following themselves."""
    alice = _create_user(db_session, "alice_self@example.com", "alice_self")

    follow_self = UserFollow(follower_id=alice.id, following_id=alice.id)
    db_session.add(follow_self)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cascade_delete_on_user_removal(db_session):
    """Verify that deleting a user removes all their associated follow relationships."""
    alice = _create_user(db_session, "alice_del@example.com", "alice_del")
    bob = _create_user(db_session, "bob_del@example.com", "bob_del")
    charlie = _create_user(db_session, "charlie_del@example.com", "charlie_del")

    # Alice follows Bob and Charlie
    db_session.add_all([
        UserFollow(follower_id=alice.id, following_id=bob.id),
        UserFollow(follower_id=alice.id, following_id=charlie.id),
        UserFollow(follower_id=charlie.id, following_id=alice.id),
    ])
    db_session.commit()

    assert db_session.scalar(select(UserFollow).where(UserFollow.follower_id == alice.id)) is not None

    # Deleting Alice should cascade and remove her follow relationships
    db_session.delete(alice)
    db_session.commit()

    # None of the records involving Alice should remain
    records = db_session.scalars(
        select(UserFollow).where(
            (UserFollow.follower_id == alice.id) | (UserFollow.following_id == alice.id)
        )
    ).all()
    assert len(records) == 0


# --- US3.5 Task 3.5.2: Follow/Unfollow Endpoints & Follower/Following Count Queries ---

def test_follow_toggle_endpoint(client):
    """Verify that POST /api/v1/users/{id}/follow toggles follow and returns updated counts."""
    alice_h = auth_headers(client, email="alice_api@example.com", username="alice_api")
    bob_h = auth_headers(client, email="bob_api@example.com", username="bob_api")

    bob_id = client.get("/api/v1/users/bob_api").json()["id"]

    # 1. Alice follows Bob -> should be following with followers_count = 1
    res = client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    assert res.status_code == 200
    data = res.json()
    assert data["following"] is True
    assert data["followers_count"] == 1
    assert data["following_count"] == 0

    # 2. Alice toggles again -> should unfollow with followers_count = 0
    res_unfollow = client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    assert res_unfollow.status_code == 200
    data_unfollow = res_unfollow.json()
    assert data_unfollow["following"] is False
    assert data_unfollow["followers_count"] == 0
    assert data_unfollow["following_count"] == 0


def test_cannot_follow_self_endpoint(client):
    """Verify HTTP 400 Bad Request when attempting to self-follow."""
    alice_h = auth_headers(client, email="self_follow@example.com", username="self_follow")
    alice_id = client.get("/api/v1/users/self_follow").json()["id"]

    res = client.post(f"/api/v1/users/{alice_id}/follow", headers=alice_h)
    assert res.status_code == 400
    assert "cannot follow yourself" in res.json()["detail"].lower()


def test_follow_nonexistent_user_returns_404(client):
    """Verify HTTP 404 when attempting to follow an unknown user id."""
    alice_h = auth_headers(client, email="alice_404@example.com", username="alice_404")
    res = client.post("/api/v1/users/999999/follow", headers=alice_h)
    assert res.status_code == 404
    assert "user not found" in res.json()["detail"].lower()


def test_unauthenticated_follow_rejected(client):
    """Verify HTTP 401 when follow endpoint is called without JWT auth token."""
    res = client.post("/api/v1/users/1/follow")
    assert res.status_code == 401


def test_get_follow_status_and_counts_endpoint(client):
    """Verify GET /api/v1/users/{id}/follow returns accurate follow status and follower counts."""
    alice_h = auth_headers(client, email="alice_counts@example.com", username="alice_counts")
    bob_h = auth_headers(client, email="bob_counts@example.com", username="bob_counts")
    charlie_h = auth_headers(client, email="charlie_counts@example.com", username="charlie_counts")

    bob_id = client.get("/api/v1/users/bob_counts").json()["id"]

    # Initial state: Bob has 0 followers, 0 following
    res_init = client.get(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    assert res_init.status_code == 200
    assert res_init.json() == {"following": False, "followers_count": 0, "following_count": 0}

    # Alice and Charlie follow Bob
    client.post(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    client.post(f"/api/v1/users/{bob_id}/follow", headers=charlie_h)

    # Bob's status viewed by Alice: Alice follows Bob, Bob has 2 followers
    res_alice_view = client.get(f"/api/v1/users/{bob_id}/follow", headers=alice_h)
    assert res_alice_view.status_code == 200
    assert res_alice_view.json() == {"following": True, "followers_count": 2, "following_count": 0}

    # Bob's status viewed unauthenticated: following is False, Bob has 2 followers
    res_anon_view = client.get(f"/api/v1/users/{bob_id}/follow")
    assert res_anon_view.status_code == 200
    assert res_anon_view.json() == {"following": False, "followers_count": 2, "following_count": 0}
