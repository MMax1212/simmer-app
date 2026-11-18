"""Tests for US3.1.2: Post Creation and Retrieval API Endpoints.

Each test is mapped directly to an acceptance criterion in docs/tasks/sprint-3/US3.1.2.md.
"""
from app.models import Recipe
from tests.conftest import auth_headers


def test_US3_1_2_criterion_1_unauthenticated_post_creation_rejected(client):
    """US3.1.2 Criterion 1: Unauthenticated request to POST /api/v1/posts returns 401."""
    payload = {
        "caption": "My fresh dinner",
        "image_url": "https://images.unsplash.com/dinner.jpg",
        "media_type": "image",
    }
    response = client.post("/api/v1/posts", json=payload)
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_US3_1_2_criterion_2_authenticated_post_creation(client, db_session):
    """US3.1.2 Criterion 2: Authenticated user creates a post and receives 201 Created."""
    headers = auth_headers(client, email="foodie@example.com", username="foodie")

    # Create a recipe first to link
    recipe = Recipe(title="Homemade Gnocchi", description="Potato pasta", author_id=1)
    db_session.add(recipe)
    db_session.commit()

    payload = {
        "caption": "Handmade potato gnocchi with brown butter sage!",
        "image_url": "https://images.unsplash.com/gnocchi.jpg",
        "media_type": "image",
        "recipe_id": recipe.id,
    }
    response = client.post("/api/v1/posts", headers=headers, json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["caption"] == "Handmade potato gnocchi with brown butter sage!"
    assert data["image_url"] == "https://images.unsplash.com/gnocchi.jpg"
    assert data["media_type"] == "image"
    assert data["author_username"] == "foodie"
    assert data["recipe_id"] == recipe.id
    assert data["recipe_title"] == "Homemade Gnocchi"
    assert "created_at" in data
    assert "updated_at" in data


def test_US3_1_2_criterion_3_missing_or_empty_media_rejected(client):
    """US3.1.2 Criterion 3: Missing or empty image_url returns HTTP 422."""
    headers = auth_headers(client, email="poster2@example.com", username="poster2")

    # Missing image_url
    res_missing = client.post("/api/v1/posts", headers=headers, json={"caption": "No image attached"})
    assert res_missing.status_code == 422

    # Empty string image_url
    res_empty = client.post("/api/v1/posts", headers=headers, json={"caption": "Empty image string", "image_url": ""})
    assert res_empty.status_code == 422

    # Empty caption
    res_no_caption = client.post(
        "/api/v1/posts", headers=headers, json={"caption": "", "image_url": "https://img.com/test.jpg"}
    )
    assert res_no_caption.status_code == 422


def test_US3_1_2_criterion_4_nonexistent_recipe_id_rejected(client):
    """US3.1.2 Criterion 4: Linking a non-existent recipe_id returns HTTP 404."""
    headers = auth_headers(client, email="poster3@example.com", username="poster3")

    payload = {
        "caption": "Linking a bogus recipe ID",
        "image_url": "https://images.unsplash.com/dish.jpg",
        "recipe_id": 999999,
    }
    response = client.post("/api/v1/posts", headers=headers, json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Linked recipe not found"


def test_US3_1_2_criterion_5_public_get_post_by_id(client, db_session):
    """US3.1.2 Criterion 5: Public GET /api/v1/posts/{id} returns 200 with full post details."""
    headers = auth_headers(client, email="creator@example.com", username="creator")

    recipe = Recipe(title="Spicy Rigatoni", description="Creamy vodka sauce", author_id=1)
    db_session.add(recipe)
    db_session.commit()

    # Create post (video review)
    created = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "caption": "Cook along video tutorial for spicy rigatoni!",
            "image_url": "https://cdn.simmer.app/videos/rigatoni.mp4",
            "media_type": "video",
            "recipe_id": recipe.id,
        },
    ).json()

    post_id = created["id"]

    # Public request (no Authorization header)
    public_res = client.get(f"/api/v1/posts/{post_id}")
    assert public_res.status_code == 200
    post_data = public_res.json()

    assert post_data["id"] == post_id
    assert post_data["author_username"] == "creator"
    assert post_data["media_type"] == "video"
    assert post_data["recipe_title"] == "Spicy Rigatoni"
    assert post_data["caption"] == "Cook along video tutorial for spicy rigatoni!"


def test_US3_1_2_criterion_6_nonexistent_post_returns_404(client):
    """US3.1.2 Criterion 6: Requesting non-existent post ID returns HTTP 404."""
    response = client.get("/api/v1/posts/888888")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
