import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.models import User
from app.models.user_follow import UserFollow


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
