"""FastAPI REST API endpoints for grocery checklists (US4.2 / Task 4.2.3)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.grocery import (
    DEFAULT_DEPARTMENT,
    DEFAULT_GROCERY_TITLE,
    GroceryItem,
    GroceryList,
)
from app.models.recipe import Recipe
from app.schemas.grocery import (
    GroceryItemCreate,
    GroceryItemOut,
    GroceryItemUpdate,
    GroceryListGenerate,
    GroceryListOut,
)
from app.services.grocery import aggregate_ingredients, classify_department

router = APIRouter(prefix="/api/v1", tags=["Grocery Checklist"])


@router.post(
    "/grocery-list/generate",
    response_model=GroceryListOut,
    status_code=status.HTTP_201_CREATED,
)
def generate_grocery_list(
    payload: GroceryListGenerate,
    db: DbSession,
    current_user: CurrentUser,
) -> GroceryList:
    """Generate a consolidated grocery checklist from selected recipe IDs."""
    recipes = db.scalars(
        select(Recipe).where(Recipe.id.in_(payload.recipe_ids))
    ).all()
    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching recipes found for the provided IDs",
        )

    raw_items = []
    for recipe in recipes:
        for ing in recipe.ingredients:
            raw_items.append({
                "name": ing.name,
                "amount": ing.amount,
                "unit": ing.unit,
                "recipe_id": recipe.id,
            })

    if not raw_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected recipes do not contain any ingredients to aggregate",
        )

    aggregated = aggregate_ingredients(raw_items)

    grocery_list = db.scalar(
        select(GroceryList).where(GroceryList.user_id == current_user.id)
    )
    if grocery_list is None:
        grocery_list = GroceryList(
            user_id=current_user.id,
            title=payload.title or DEFAULT_GROCERY_TITLE,
        )
        db.add(grocery_list)
        db.flush()
    else:
        grocery_list.title = payload.title or grocery_list.title
        grocery_list.updated_at = datetime.now(timezone.utc)
        grocery_list.items.clear()
        db.flush()

    for agg in aggregated:
        item = GroceryItem(
            grocery_list_id=grocery_list.id,
            name=agg["name"],
            amount=agg["amount"],
            unit=agg["unit"],
            department=agg["department"],
            source_recipe_id=agg.get("source_recipe_id"),
            is_checked=False,
        )
        db.add(item)

    db.commit()
    db.refresh(grocery_list)
    return grocery_list


@router.get("/grocery-list", response_model=GroceryListOut)
def get_grocery_list(
    db: DbSession,
    current_user: CurrentUser,
) -> GroceryList:
    """Retrieve the authenticated user's active grocery checklist."""
    grocery_list = db.scalar(
        select(GroceryList).where(GroceryList.user_id == current_user.id)
    )
    if grocery_list is None:
        grocery_list = GroceryList(
            user_id=current_user.id,
            title=DEFAULT_GROCERY_TITLE,
        )
        db.add(grocery_list)
        db.commit()
        db.refresh(grocery_list)
    return grocery_list


@router.patch("/grocery-items/{id}", response_model=GroceryItemOut)
def update_grocery_item(
    id: int,
    payload: GroceryItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> GroceryItem:
    """Toggle item completion status or update quantity/name."""
    item = db.get(GroceryItem, id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery item not found",
        )
    if item.grocery_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this grocery item",
        )

    if payload.is_checked is not None:
        item.is_checked = payload.is_checked
    if payload.amount is not None:
        item.amount = payload.amount
    if payload.name is not None:
        item.name = payload.name

    item.grocery_list.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.post(
    "/grocery-items",
    response_model=GroceryItemOut,
    status_code=status.HTTP_201_CREATED,
)
def add_custom_grocery_item(
    payload: GroceryItemCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> GroceryItem:
    """Add a manual custom item directly to the user's checklist."""
    grocery_list = db.scalar(
        select(GroceryList).where(GroceryList.user_id == current_user.id)
    )
    if grocery_list is None:
        grocery_list = GroceryList(
            user_id=current_user.id,
            title=DEFAULT_GROCERY_TITLE,
        )
        db.add(grocery_list)
        db.flush()

    dept = (
        payload.department
        if payload.department and payload.department != DEFAULT_DEPARTMENT
        else classify_department(payload.name)
    )

    item = GroceryItem(
        grocery_list_id=grocery_list.id,
        name=payload.name,
        amount=payload.amount,
        unit=payload.unit,
        department=dept,
        source_recipe_id=payload.source_recipe_id,
        is_checked=False,
    )
    db.add(item)
    grocery_list.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/grocery-items/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grocery_item(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Remove an item from the grocery checklist."""
    item = db.get(GroceryItem, id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery item not found",
        )
    if item.grocery_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this grocery item",
        )

    grocery_list = item.grocery_list
    grocery_list.updated_at = datetime.now(timezone.utc)
    db.delete(item)
    db.commit()
    return None
