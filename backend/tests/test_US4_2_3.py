"""Tests for US4.2.3: Backend Grocery Checklist REST API Endpoints.

Mapped directly to acceptance criteria in docs/tasks/sprint-4/US4.2.3.md.
"""
from __future__ import annotations

import pytest
from app.models import Ingredient, Recipe, User
from tests.conftest import auth_headers


def test_US4_2_3_criterion_1_generate_grocery_list(client, db_session):
    """Criterion 1: POST /api/v1/grocery-list/generate creates aggregated checklist."""
    headers = auth_headers(client, email="chef1@test.com", username="chef1")
    user = db_session.query(User).filter_by(username="chef1").first()

    # Create two recipes with overlapping ingredients
    r1 = Recipe(title="Garlic Pasta", author_id=user.id)
    r2 = Recipe(title="Garlic Bread", author_id=user.id)
    db_session.add_all([r1, r2])
    db_session.flush()

    ing1 = Ingredient(recipe_id=r1.id, name="olive oil", amount=0.5, unit="cup")
    ing2 = Ingredient(recipe_id=r2.id, name="extra virgin olive oil", amount=0.25, unit="cup")
    ing3 = Ingredient(recipe_id=r1.id, name="garlic", amount=3.0, unit="clove")
    db_session.add_all([ing1, ing2, ing3])
    db_session.commit()

    resp = client.post(
        "/api/v1/grocery-list/generate",
        headers=headers,
        json={"recipe_ids": [r1.id, r2.id], "title": "Dinner Prep"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Dinner Prep"
    assert len(data["items"]) == 2

    # Check olive oil combined to 0.75 cup in Pantry & Baking
    oil_item = next(i for i in data["items"] if i["name"] == "olive oil")
    assert oil_item["amount"] == 0.75
    assert oil_item["unit"] == "cup"
    assert oil_item["department"] == "Pantry & Baking"


def test_US4_2_3_criterion_2_get_grocery_list(client, db_session):
    """Criterion 2: GET /api/v1/grocery-list retrieves the authenticated user's checklist."""
    headers = auth_headers(client, email="chef2@test.com", username="chef2")

    resp = client.get("/api/v1/grocery-list", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "My Grocery List"
    assert "items" in data


def test_US4_2_3_criterion_3_patch_grocery_item(client, db_session):
    """Criterion 3: PATCH /api/v1/grocery-items/{id} updates check state and quantity."""
    headers = auth_headers(client, email="chef3@test.com", username="chef3")

    # Add item
    add_resp = client.post(
        "/api/v1/grocery-items",
        headers=headers,
        json={"name": "whole milk", "amount": 1.0, "unit": "gallon"},
    )
    item_id = add_resp.json()["id"]

    # Toggle checked
    patch_resp = client.patch(
        f"/api/v1/grocery-items/{item_id}",
        headers=headers,
        json={"is_checked": True, "amount": 2.0},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["is_checked"] is True
    assert updated["amount"] == 2.0


def test_US4_2_3_criterion_4_add_custom_item_with_auto_department(client, db_session):
    """Criterion 4: POST /api/v1/grocery-items adds manual item with auto department."""
    headers = auth_headers(client, email="chef4@test.com", username="chef4")

    resp = client.post(
        "/api/v1/grocery-items",
        headers=headers,
        json={"name": "fresh strawberries", "amount": 2.0, "unit": "cup"},
    )
    assert resp.status_code == 201
    item = resp.json()
    assert item["name"] == "fresh strawberries"
    assert item["department"] == "Produce"


def test_US4_2_3_criterion_5_delete_grocery_item(client, db_session):
    """Criterion 5: DELETE /api/v1/grocery-items/{id} removes an item returning 204."""
    headers = auth_headers(client, email="chef5@test.com", username="chef5")

    add_resp = client.post(
        "/api/v1/grocery-items",
        headers=headers,
        json={"name": "apples", "amount": 4.0, "unit": "piece"},
    )
    item_id = add_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/grocery-items/{item_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify item is removed from the user's checklist
    list_resp = client.get("/api/v1/grocery-list", headers=headers)
    item_ids = [i["id"] for i in list_resp.json()["items"]]
    assert item_id not in item_ids


def test_US4_2_3_criterion_6_cross_user_protection(client, db_session):
    """Criterion 6: Non-owners cannot update or delete other users' grocery items."""
    user1_headers = auth_headers(client, email="owner@test.com", username="owner")
    user2_headers = auth_headers(client, email="other@test.com", username="other")

    add_resp = client.post(
        "/api/v1/grocery-items",
        headers=user1_headers,
        json={"name": "eggs", "amount": 12.0, "unit": "piece"},
    )
    item_id = add_resp.json()["id"]

    # user2 attempts to patch user1's item -> 403 Forbidden
    patch_resp = client.patch(
        f"/api/v1/grocery-items/{item_id}",
        headers=user2_headers,
        json={"is_checked": True},
    )
    assert patch_resp.status_code == 403

    # user2 attempts to delete user1's item -> 403 Forbidden
    del_resp = client.delete(f"/api/v1/grocery-items/{item_id}", headers=user2_headers)
    assert del_resp.status_code == 403
