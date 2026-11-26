"""Pydantic DTO schemas for grocery checklists and checklist items (US4.2 / Task 4.2.3)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_ITEM_DEPARTMENT: str = "Other"
DEFAULT_LIST_TITLE: str = "My Grocery List"
MAX_NAME_LENGTH: int = 100
MAX_UNIT_LENGTH: int = 30
MAX_DEPARTMENT_LENGTH: int = 50
MAX_TITLE_LENGTH: int = 100
MIN_RECIPES_TO_GENERATE: int = 1
MAX_RECIPES_TO_GENERATE: int = 20


class GroceryItemCreate(BaseModel):
    """Payload to add a manual custom item directly to a grocery checklist."""

    name: str = Field(..., min_length=1, max_length=MAX_NAME_LENGTH)
    amount: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=MAX_UNIT_LENGTH)
    department: Optional[str] = Field(
        DEFAULT_ITEM_DEPARTMENT, max_length=MAX_DEPARTMENT_LENGTH
    )
    source_recipe_id: Optional[int] = None


class GroceryItemUpdate(BaseModel):
    """Payload to update an item's completion status, quantity, or name."""

    is_checked: Optional[bool] = None
    amount: Optional[float] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)


class GroceryItemOut(BaseModel):
    """Response DTO for an individual grocery checklist item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    grocery_list_id: int
    name: str
    amount: float
    unit: str
    department: str
    is_checked: bool
    source_recipe_id: Optional[int] = None
    created_at: datetime


class GroceryListGenerate(BaseModel):
    """Payload to generate a consolidated checklist from selected recipes."""

    recipe_ids: list[int] = Field(
        ...,
        min_length=MIN_RECIPES_TO_GENERATE,
        max_length=MAX_RECIPES_TO_GENERATE,
    )
    title: Optional[str] = Field(DEFAULT_LIST_TITLE, max_length=MAX_TITLE_LENGTH)


class GroceryListOut(BaseModel):
    """Response DTO for a user's grocery checklist with aggregated items."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    items: list[GroceryItemOut]
    created_at: datetime
    updated_at: datetime
