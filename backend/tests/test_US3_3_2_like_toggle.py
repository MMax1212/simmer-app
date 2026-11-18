"""Tests for US3.3.2: Post Like Toggle and Count API Endpoint.

Mapped directly to acceptance criteria in docs/tasks/sprint-3/US3.3.2.md.
"""
from app.models import Post, PostLike, User
from tests.conftest import auth_headers


def _create_test_post(db_session, author_email="author@example.com", author_user="author"):
    """Helper to create a user and a post in the database."""
    author = User(email=author_email, username=author_user, hashed_password="pw")
    db_session.add(author)
    db_session.commit()

    post = Post(
        author_id=author.id,
        caption="Crispy fried chicken",
        image_url="https://images.unsplash.com/chicken.jpg",
    )
    db_session.add(post)
    db_session.commit()
    return post


def test_US3_3_2_criterion_1_unauthenticated_like_rejected(client, db_session):
    """US3.3.2 Criterion 1: POST /api/v1/posts/{id}/like requires auth and returns 401."""
    post = _create_test_post(db_session)
    response = client.post(f"/api/v1/posts/{post.id}/like")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_US3_3_2_criterion_2_like_nonexistent_post_returns_404(client, db_session):
    """US3.3.2 Criterion 2: Attempting to like a non-existent post ID returns 404."""
    headers = auth_headers(client, email="user@example.com", username="user")
    response = client.post("/api/v1/posts/99999/like", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_US3_3_2_criterion_3_authenticated_like_unliked_post_increments_count(client, db_session):
    """US3.3.2 Criterion 3: Authenticated user liking an unliked post returns HTTP 200 with liked=True and likes_count=1."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="liker1@example.com", username="liker1")

    response = client.post(f"/api/v1/posts/{post.id}/like", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["liked"] is True
    assert data["likes_count"] == 1

    # Verify persisted in database
    likes = db_session.query(PostLike).filter_by(post_id=post.id).all()
    assert len(likes) == 1


def test_US3_3_2_criterion_4_like_already_liked_post_unlikes_and_decrements_count(client, db_session):
    """US3.3.2 Criterion 4: Calling the endpoint a second time unlikes and returns liked=False and likes_count=0."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="liker2@example.com", username="liker2")

    # First like
    res1 = client.post(f"/api/v1/posts/{post.id}/like", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["liked"] is True
    assert res1.json()["likes_count"] == 1

    # Second like (toggles off / unlikes)
    res2 = client.post(f"/api/v1/posts/{post.id}/like", headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["liked"] is False
    assert data2["likes_count"] == 0

    # Verify removed from database
    likes = db_session.query(PostLike).filter_by(post_id=post.id).all()
    assert len(likes) == 0


def test_US3_3_2_criterion_5_multiple_users_like_same_post(client, db_session):
    """US3.3.2 Criterion 5: Multiple distinct users liking the same post increments likes_count accurately."""
    post = _create_test_post(db_session)
    headers_user1 = auth_headers(client, email="fan1@example.com", username="fan1")
    headers_user2 = auth_headers(client, email="fan2@example.com", username="fan2")
    headers_user3 = auth_headers(client, email="fan3@example.com", username="fan3")

    # User 1 likes -> 1
    r1 = client.post(f"/api/v1/posts/{post.id}/like", headers=headers_user1)
    assert r1.status_code == 200
    assert r1.json() == {"liked": True, "likes_count": 1}

    # User 2 likes -> 2
    r2 = client.post(f"/api/v1/posts/{post.id}/like", headers=headers_user2)
    assert r2.status_code == 200
    assert r2.json() == {"liked": True, "likes_count": 2}

    # User 3 likes -> 3
    r3 = client.post(f"/api/v1/posts/{post.id}/like", headers=headers_user3)
    assert r3.status_code == 200
    assert r3.json() == {"liked": True, "likes_count": 3}

    # User 2 unlikes -> 2
    r2_unlike = client.post(f"/api/v1/posts/{post.id}/like", headers=headers_user2)
    assert r2_unlike.status_code == 200
    assert r2_unlike.json() == {"liked": False, "likes_count": 2}


def test_US3_3_2_criterion_6_toggle_only_affects_calling_user(client, db_session):
    """US3.3.2 Criterion 6: Only the calling user's like is toggled without removing other users' likes."""
    post = _create_test_post(db_session)
    headers_alice = auth_headers(client, email="alice@example.com", username="alice")
    headers_bob = auth_headers(client, email="bob@example.com", username="bob")

    # Both like the post
    client.post(f"/api/v1/posts/{post.id}/like", headers=headers_alice)
    client.post(f"/api/v1/posts/{post.id}/like", headers=headers_bob)

    # Alice unlikes
    res = client.post(f"/api/v1/posts/{post.id}/like", headers=headers_alice)
    assert res.json()["liked"] is False
    assert res.json()["likes_count"] == 1

    # Bob's like must still exist
    bob_user = db_session.query(User).filter_by(username="bob").one()
    bob_like = db_session.query(PostLike).filter_by(post_id=post.id, user_id=bob_user.id).one_or_none()
    assert bob_like is not None


def test_US3_3_2_criterion_7_response_schema_contract(client, db_session):
    """US3.3.2 Criterion 7: Response matches LikeToggleResponse schema structure."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="contract_user@example.com", username="contract_user")

    response = client.post(f"/api/v1/posts/{post.id}/like", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["liked"], bool)
    assert isinstance(data["likes_count"], int)
    assert set(data.keys()) == {"liked", "likes_count"}
