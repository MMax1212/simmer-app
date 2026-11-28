import pytest
from sqlalchemy import select
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


def _follow(db, follower_id: int, following_id: int):
    follow = UserFollow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    db.commit()


# --- US4.1 Task 4.1.5: Suggested Cooks to Follow Tests ---

def test_suggested_cooks_unauthenticated_ranks_by_popularity(client, db_session):
    """Unauthenticated guests receive suggestions ordered by follower count descending."""
    chef_a = _create_user(db_session, "chef_a@example.com", "chef_a")
    chef_b = _create_user(db_session, "chef_b@example.com", "chef_b")
    chef_c = _create_user(db_session, "chef_c@example.com", "chef_c")
    fan1 = _create_user(db_session, "fan1@example.com", "fan1")
    fan2 = _create_user(db_session, "fan2@example.com", "fan2")

    # chef_b has 2 followers, chef_a has 1 follower, chef_c has 0
    _follow(db_session, fan1.id, chef_b.id)
    _follow(db_session, fan2.id, chef_b.id)
    _follow(db_session, fan1.id, chef_a.id)

    res = client.get("/api/v1/users/suggested?limit=3")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    # chef_b is first (2 followers), chef_a second (1 follower)
    assert data[0]["username"] == "chef_b"
    assert data[0]["followers_count"] == 2
    assert data[1]["username"] == "chef_a"
    assert data[1]["followers_count"] == 1


def test_suggested_cooks_excludes_self_and_already_followed(client, db_session):
    """Authenticated user is excluded from suggestions, as are users they already follow."""
    headers = auth_headers(client, "alice@example.com", "alice")
    alice = db_session.scalar(select(User).where(User.username == "alice"))
    bob = _create_user(db_session, "bob@example.com", "bob")
    charlie = _create_user(db_session, "charlie@example.com", "charlie")
    diana = _create_user(db_session, "diana@example.com", "diana")

    # Alice already follows Bob
    _follow(db_session, alice.id, bob.id)
    # Diana follows Charlie
    _follow(db_session, diana.id, charlie.id)

    res = client.get("/api/v1/users/suggested", headers=headers)
    assert res.status_code == 200
    data = res.json()
    suggested_usernames = [u["username"] for u in data]

    # Neither Alice (self) nor Bob (already followed) should appear
    assert "alice" not in suggested_usernames
    assert "bob" not in suggested_usernames
    assert "charlie" in suggested_usernames
    assert "diana" in suggested_usernames


def test_suggested_cooks_prioritizes_mutual_follows(client, db_session):
    """Prioritizes creators followed by users that the caller follows (2nd degree connections)."""
    headers = auth_headers(client, "alice_s@example.com", "alice_s")
    alice = db_session.scalar(select(User).where(User.username == "alice_s"))
    bob = _create_user(db_session, "bob_s@example.com", "bob_s")
    charlie = _create_user(db_session, "charlie_s@example.com", "charlie_s")
    david = _create_user(db_session, "david_s@example.com", "david_s")  # mutual follow target
    stranger = _create_user(db_session, "stranger@example.com", "stranger")

    # Alice follows Bob and Charlie
    _follow(db_session, alice.id, bob.id)
    _follow(db_session, alice.id, charlie.id)

    # Bob AND Charlie both follow David (David has 2 mutual connections from Alice)
    _follow(db_session, bob.id, david.id)
    _follow(db_session, charlie.id, david.id)

    # Some fans follow Stranger so stranger has followers, but not mutual from Alice
    fan1 = _create_user(db_session, "fan1_s@example.com", "fan1_s")
    _follow(db_session, fan1.id, stranger.id)

    res = client.get("/api/v1/users/suggested", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # David must be ranked first because he has mutual follows from Alice's network
    assert data[0]["username"] == "david_s"
    assert data[0]["followers_count"] == 2


def test_suggested_cooks_excludes_deactivated_users(client, db_session):
    """Deactivated accounts are never returned as suggestions."""
    active_chef = _create_user(db_session, "active_c@example.com", "active_c", is_active=True)
    inactive_chef = _create_user(db_session, "inactive_c@example.com", "inactive_c", is_active=False)

    res = client.get("/api/v1/users/suggested")
    assert res.status_code == 200
    usernames = [u["username"] for u in res.json()]
    assert "active_c" in usernames
    assert "inactive_c" not in usernames
