"""Tests for US3.3.3: Post Comments Creation, Listing, and Deletion API Endpoints.

Mapped directly to acceptance criteria in docs/tasks/sprint-3/US3.3.3.md.
"""
from app.models import Post, PostComment, User
from tests.conftest import auth_headers


def _create_test_post(db_session, author_email="postauthor@example.com", author_user="postauthor"):
    """Helper to create a user and a post in the database."""
    author = User(email=author_email, username=author_user, hashed_password="pw")
    db_session.add(author)
    db_session.commit()

    post = Post(
        author_id=author.id,
        caption="Homemade sourdough bread",
        image_url="https://images.unsplash.com/bread.jpg",
    )
    db_session.add(post)
    db_session.commit()
    return post


def test_US3_3_3_criterion_1_unauthenticated_comment_actions_rejected(client, db_session):
    """US3.3.3 AC1: POST comment and DELETE comment require authentication (return 401)."""
    post = _create_test_post(db_session)
    # POST comment without auth
    res_post = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Looks delicious!"})
    assert res_post.status_code == 401
    assert "WWW-Authenticate" in res_post.headers

    # DELETE comment without auth
    res_del = client.delete("/api/v1/comments/1")
    assert res_del.status_code == 401
    assert "WWW-Authenticate" in res_del.headers


def test_US3_3_3_criterion_2_post_existence_validation(client, db_session):
    """US3.3.3 AC2: Non-existent post ID returns 404 for listing and creating comments."""
    headers = auth_headers(client, email="commenter@example.com", username="commenter")

    # List comments on non-existent post
    res_get = client.get("/api/v1/posts/99999/comments")
    assert res_get.status_code == 404
    assert res_get.json()["detail"] == "Post not found"

    # Create comment on non-existent post
    res_create = client.post("/api/v1/posts/99999/comments", json={"content": "Hello!"}, headers=headers)
    assert res_create.status_code == 404
    assert res_create.json()["detail"] == "Post not found"


def test_US3_3_3_criterion_3_create_comment_success(client, db_session):
    """US3.3.3 AC3: Authenticated user creates a comment, returns 201 with CommentOut DTO."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="chef_anna@example.com", username="chef_anna")

    payload = {"content": "What oven temperature did you use?"}
    response = client.post(f"/api/v1/posts/{post.id}/comments", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert data["post_id"] == post.id
    assert data["username"] == "chef_anna"
    assert data["content"] == "What oven temperature did you use?"
    assert "id" in data
    assert "created_at" in data
    assert "avatar_url" in data

    # Verify persisted in database
    comment = db_session.get(PostComment, data["id"])
    assert comment is not None
    assert comment.content == "What oven temperature did you use?"
    assert comment.post_id == post.id


def test_US3_3_3_criterion_4_content_validation(client, db_session):
    """US3.3.3 AC4: Empty, whitespace-only, or overly long content is rejected with 422."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="validuser@example.com", username="validuser")

    # Empty string
    r_empty = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": ""}, headers=headers)
    assert r_empty.status_code == 422

    # Whitespace only
    r_space = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "   \n\t  "}, headers=headers)
    assert r_space.status_code == 422

    # Exceeding 1000 characters
    r_long = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "a" * 1001}, headers=headers)
    assert r_long.status_code == 422


def test_US3_3_3_criterion_5_list_comments_chronological_and_pagination(client, db_session):
    """US3.3.3 AC5: GET comments returns comments in chronological order and supports pagination."""
    post = _create_test_post(db_session)
    headers1 = auth_headers(client, email="user1@example.com", username="user1")
    headers2 = auth_headers(client, email="user2@example.com", username="user2")

    # Post comments in sequence
    r1 = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "First comment!"}, headers=headers1)
    r2 = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Second comment!"}, headers=headers2)
    r3 = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Third comment!"}, headers=headers1)
    assert r1.status_code == 201 and r2.status_code == 201 and r3.status_code == 201

    # List all comments
    res = client.get(f"/api/v1/posts/{post.id}/comments")
    assert res.status_code == 200
    comments = res.json()
    assert len(comments) == 3
    assert [c["content"] for c in comments] == ["First comment!", "Second comment!", "Third comment!"]
    assert comments[0]["username"] == "user1"
    assert comments[1]["username"] == "user2"
    assert comments[2]["username"] == "user1"

    # Test limit and offset pagination
    res_page = client.get(f"/api/v1/posts/{post.id}/comments?limit=2&offset=1")
    assert res_page.status_code == 200
    page_comments = res_page.json()
    assert len(page_comments) == 2
    assert page_comments[0]["content"] == "Second comment!"
    assert page_comments[1]["content"] == "Third comment!"


def test_US3_3_3_criterion_6_author_can_delete_comment(client, db_session):
    """US3.3.3 AC6: The author of a comment can delete it, returning 204 No Content."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="author_del@example.com", username="author_del")

    # Create comment
    c_res = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Typo to delete"}, headers=headers)
    comment_id = c_res.json()["id"]

    # Delete via DELETE /api/v1/comments/{id}
    del_res = client.delete(f"/api/v1/comments/{comment_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify no longer returned in list
    list_res = client.get(f"/api/v1/posts/{post.id}/comments")
    assert len(list_res.json()) == 0

    # Verify removed from database
    assert db_session.get(PostComment, comment_id) is None


def test_US3_3_3_criterion_7_admin_can_delete_any_comment(client, db_session, make_admin):
    """US3.3.3 AC7: An admin can delete another user's comment, returning 204 No Content."""
    post = _create_test_post(db_session)
    user_headers = auth_headers(client, email="regular@example.com", username="regular")
    admin_headers = auth_headers(client, email="moderator@example.com", username="moderator")
    make_admin("moderator@example.com")

    # Regular user creates comment
    c_res = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Spam message"}, headers=user_headers)
    comment_id = c_res.json()["id"]

    # Admin deletes comment
    del_res = client.delete(f"/api/v1/comments/{comment_id}", headers=admin_headers)
    assert del_res.status_code == 204

    # Verify removed
    assert db_session.get(PostComment, comment_id) is None


def test_US3_3_3_criterion_8_non_admin_cannot_delete_others_comment(client, db_session):
    """US3.3.3 AC8: Non-author, non-admin user receives 403 Forbidden attempting deletion."""
    post = _create_test_post(db_session)
    alice_headers = auth_headers(client, email="alice_c@example.com", username="alice_c")
    bob_headers = auth_headers(client, email="bob_c@example.com", username="bob_c")

    # Alice creates comment
    c_res = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Alice's comment"}, headers=alice_headers)
    comment_id = c_res.json()["id"]

    # Bob attempts to delete Alice's comment
    del_res = client.delete(f"/api/v1/comments/{comment_id}", headers=bob_headers)
    assert del_res.status_code == 403
    assert del_res.json()["detail"] == "Not authorized to delete this comment"

    # Comment still exists
    assert db_session.get(PostComment, comment_id) is not None


def test_US3_3_3_criterion_9_delete_nonexistent_comment_returns_404(client, db_session):
    """US3.3.3 AC9: Deleting non-existent comment ID returns 404 Not Found."""
    headers = auth_headers(client, email="someone@example.com", username="someone")
    del_res = client.delete("/api/v1/comments/99999", headers=headers)
    assert del_res.status_code == 404
    assert del_res.json()["detail"] == "Comment not found"


def test_US3_3_3_criterion_10_post_scoped_delete_route(client, db_session):
    """US3.3.3 AC10: Author can also delete via DELETE /api/v1/posts/{post_id}/comments/{comment_id}."""
    post = _create_test_post(db_session)
    headers = auth_headers(client, email="scoped_del@example.com", username="scoped_del")

    # Create comment
    c_res = client.post(f"/api/v1/posts/{post.id}/comments", json={"content": "Scoped delete test"}, headers=headers)
    comment_id = c_res.json()["id"]

    # Delete via post-scoped route
    del_res = client.delete(f"/api/v1/posts/{post.id}/comments/{comment_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify removed
    assert db_session.get(PostComment, comment_id) is None
