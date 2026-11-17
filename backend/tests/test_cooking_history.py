from datetime import datetime, timedelta, timezone

from app.models import CompletedRecipe
from tests.conftest import auth_headers
from tests.test_recipes import PASTA


# --- US2.3 Task 2.3.5: Cooking History Integration Tests ---

def test_log_recipe_as_cooked_success(client):
    """Authenticated users can mark a recipe as cooked with optional rating and notes."""
    h = auth_headers(client, email="chef@example.com", username="chef")
    recipe = client.post("/api/v1/recipes", headers=h, json=PASTA).json()
    recipe_id = recipe["id"]

    payload = {"notes": "Substituted almond flour, turned out crispy!", "rating": 5}
    res = client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["recipe_id"] == recipe_id
    assert data["notes"] == "Substituted almond flour, turned out crispy!"
    assert data["rating"] == 5
    assert "cooked_at" in data
    assert "id" in data


def test_duplicate_cooked_log_prevented_within_60_seconds(client):
    """Prevent double-clicking 'I Cooked This!' within a 60-second window."""
    h = auth_headers(client, email="repeat@example.com", username="repeater")
    recipe_id = client.post("/api/v1/recipes", headers=h, json=PASTA).json()["id"]

    # First log succeeds
    first = client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": 4})
    assert first.status_code == 201

    # Immediate duplicate attempt within 60s is rejected
    duplicate = client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": 4})
    assert duplicate.status_code == 400
    assert "60 seconds" in duplicate.json()["detail"]


def test_duplicate_check_allows_cooking_again_after_window(client, db_session):
    """Logging the same recipe again after 60 seconds is allowed."""
    h = auth_headers(client, email="again@example.com", username="cookagain")
    recipe_id = client.post("/api/v1/recipes", headers=h, json=PASTA).json()["id"]

    # First log
    res = client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": 5})
    assert res.status_code == 201

    # Simulate past timestamp (>60 seconds ago)
    entry = db_session.query(CompletedRecipe).filter_by(recipe_id=recipe_id).first()
    entry.cooked_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    db_session.commit()

    # Second log should now succeed
    second = client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"notes": "Cooked again!", "rating": 5})
    assert second.status_code == 201


def test_log_cooked_nonexistent_recipe_404(client):
    """Logging a non-existent recipe returns 404 Not Found."""
    h = auth_headers(client, email="user@example.com", username="tester")
    res = client.post("/api/v1/recipes/99999/complete", headers=h, json={})
    assert res.status_code == 404
    assert res.json()["detail"] == "Recipe not found"


def test_log_cooked_invalid_rating_rejected(client):
    """Ratings outside 1-5 are rejected with 422 Unprocessable Entity."""
    h = auth_headers(client, email="rater@example.com", username="rater")
    recipe_id = client.post("/api/v1/recipes", headers=h, json=PASTA).json()["id"]

    assert client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": 0}).status_code == 422
    assert client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": 6}).status_code == 422
    assert client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": -1}).status_code == 422


def test_log_cooked_unauthenticated_rejected(client):
    """Unauthenticated requests are rejected with 401 Unauthorized."""
    assert client.post("/api/v1/recipes/1/complete", json={}).status_code == 401
    assert client.get("/api/v1/users/me/cooking-history").status_code == 401


def test_get_cooking_history_user_scoped_and_ordered(client, db_session):
    """Cooking history returns only the authenticated user's records in reverse-chronological order."""
    user1_h = auth_headers(client, email="u1@example.com", username="userone")
    user2_h = auth_headers(client, email="u2@example.com", username="usertwo")

    r1_id = client.post("/api/v1/recipes", headers=user1_h, json={**PASTA, "title": "First Pasta"}).json()["id"]
    r2_id = client.post("/api/v1/recipes", headers=user1_h, json={**PASTA, "title": "Second Curry"}).json()["id"]

    # User 1 cooks Recipe 1 (yesterday)
    res1 = client.post(f"/api/v1/recipes/{r1_id}/complete", headers=user1_h, json={"rating": 4, "notes": "Good"}).json()
    # User 1 cooks Recipe 2 (today)
    res2 = client.post(f"/api/v1/recipes/{r2_id}/complete", headers=user1_h, json={"rating": 5, "notes": "Great"}).json()

    # User 2 cooks Recipe 1
    client.post(f"/api/v1/recipes/{r1_id}/complete", headers=user2_h, json={"rating": 3, "notes": "Okay"})

    # Manually backdate entry 1 so entry 2 is strictly newer
    e1 = db_session.get(CompletedRecipe, res1["id"])
    e1.cooked_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()

    # User 1 fetches history
    history = client.get("/api/v1/users/me/cooking-history", headers=user1_h).json()
    assert len(history) == 2
    # Verify descending chronological order (newest first)
    assert history[0]["recipe_title"] == "Second Curry"
    assert history[0]["rating"] == 5
    assert history[1]["recipe_title"] == "First Pasta"
    assert history[1]["rating"] == 4

    # User 2 fetches history - only sees their own 1 item
    u2_history = client.get("/api/v1/users/me/cooking-history", headers=user2_h).json()
    assert len(u2_history) == 1
    assert u2_history[0]["recipe_title"] == "First Pasta"
    assert u2_history[0]["notes"] == "Okay"


def test_cascade_delete_removes_cooking_history(client):
    """Deleting a recipe cascades and deletes its completed cooking history records."""
    h = auth_headers(client, email="delete_test@example.com", username="deleter")
    recipe_id = client.post("/api/v1/recipes", headers=h, json=PASTA).json()["id"]

    client.post(f"/api/v1/recipes/{recipe_id}/complete", headers=h, json={"rating": 5})
    assert len(client.get("/api/v1/users/me/cooking-history", headers=h).json()) == 1

    # Delete the recipe
    del_res = client.delete(f"/api/v1/recipes/{recipe_id}", headers=h)
    assert del_res.status_code == 204

    # Cooking history should now be empty due to ON DELETE CASCADE
    assert len(client.get("/api/v1/users/me/cooking-history", headers=h).json()) == 0
