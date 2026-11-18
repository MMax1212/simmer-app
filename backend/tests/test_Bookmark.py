from app.models import User
from tests.conftest import auth_headers, create_test_post

def test_bookmark_toggle(client, db_session):
    """US3.4: Authenticated user can bookmark and unbookmark a post."""
    
    #Create user
    alice_headers = auth_headers(client, email="alice@example.com", username="alice")
    alice = db_session.query(User).filter_by(username="alice").one()

    #create test post in DB
    post = create_test_post(db_session,author_id=alice.id, caption="Pasta night!")

    #bookmark post
    res = client.post(f"/api/v1/posts/{post.id}/bookmark", headers=alice_headers)
    assert res.status_code == 200
    assert res.json()["bookmark"] is True

    #unbookmark post
    res = client.post(f"/api/v1/posts/{post.id}/bookmark", headers=alice_headers)
    assert res.status_code == 200
    assert res.json()["bookmark"] is False

def test_User_Isolation(client, db_session):
    """User Isolation: Alice's bookmarks do not show up in Bob's saved posts list."""

    #create users: Alice and Bob
    alice_headers = auth_headers(client, email="alice_iso@example.com", username="alice_iso")
    alice = db_session.query(User).filter_by(username="alice_iso").one()
    
    bob_headers = auth_headers(client, email="bob_iso@example.com", username="bob_iso")

    #Create post and have Alice bookmark it
    post = create_test_post(db_session, author_id=alice.id, caption="Alice's pie")
    client.post(f"/api/v1/posts/{post.id}/bookmark", headers=alice_headers)
    
    #Bob checks hsi saved post and should bae empty
    bob_res = client.get("/api/v1/users/me/saved-posts", headers=bob_headers)
    assert bob_res.status_code == 200
    bob_items = bob_res.json()["items"] if "items" in bob_res.json() else bob_res.json()
    assert len(bob_items) == 0

    #Alice checks her bookmarks/saved-posts and has her bookmarked post
    alice_res = client.get("/api/v1/users/me/saved-posts", headers=alice_headers)
    assert alice_res.status_code == 200
    alice_items = alice_res.json()["items"] if "items" in alice_res.json() else alice_res.json()
    assert len(alice_items) == 1
    assert alice_items[0]["id"] == post.id

def test_deleted_post_handling(client, db_session):
    """Cascading: Deleting a post removes it froma saved posts."""

    alice_headers = auth_headers(client, email="alice_del@example.com", username="alice_del")
    alice = db_session.query(User).filter_by(username="alice_del").one()
    post = create_test_post(db_session, author_id=alice.id, caption="Temporary post")

    client.post(f"/api/v1/posts/{post.id}/bookmark", headers=alice_headers)

    db_session.delete(post)
    db_session.commit()

    res = client.get("/api/v1/users/me/saved-posts", headers=alice_headers)
    assert res.status_code == 200
    items = res.json()["items"] if "items" in res.json() else res.json()
    assert len(items) == 0


