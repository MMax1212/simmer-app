from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IngredientIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)


class IngredientOut(IngredientIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RecipeBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    instructions: str = Field(min_length=1)
    prep_time_mins: int | None = Field(default=None, ge=0, le=10000)
    cook_time_mins: int | None = Field(default=None, ge=0, le=10000)
    servings: int | None = Field(default=None, ge=1, le=100)


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientIn] = []


class RecipeUpdate(RecipeCreate):
    """PUT replaces the whole recipe, including its ingredient list."""


class RecipeOut(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    owner_username: str
    ingredients: list[IngredientOut]
    created_at: datetime
    updated_at: datetime
