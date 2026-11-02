from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from app.schemas.user import RequestModel


# --- US1.4: Recipe Creation & Saving (Ingredient Input Schema) ---
class IngredientIn(RequestModel):
    name: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0, allow_inf_nan=False)
    unit: str = Field(min_length=1, max_length=30)

    @field_validator("name", "unit")
    @classmethod
    def strip_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be blank")
        return value.strip()


# --- US1.5: Personal Recipe Tab (Ingredient Output Schema) ---
class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    # Preserve unknown measurements in legacy recipes rather than inventing data.
    amount: float | None
    unit: str | None


# --- US1.4: Recipe Creation & Saving (Recipe Step Input Schema) ---
class RecipeStepIn(RequestModel):
    step_number: int = Field(ge=1)
    instruction: str = Field(min_length=3, max_length=10000)

    @field_validator("instruction")
    @classmethod
    def strip_instruction(cls, value: str) -> str:
        if len(value.strip()) < 3:
            raise ValueError("Instructions must contain at least 3 characters")
        return value.strip()


# --- US1.5: Personal Recipe Tab (Recipe Step Output Schema) ---
class RecipeStepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    step_number: int
    instruction: str


# --- US1.4: Recipe Creation & Saving (Recipe Creation Schema) ---
class RecipeCreate(RequestModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    cuisine: str | None = Field(default=None, max_length=50)
    meal_type: str | None = Field(default=None, max_length=50)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    image_url: str | None = Field(default=None, max_length=255)
    prep_time_mins: int = Field(default=0, ge=0, le=10000)
    cook_time_mins: int = Field(default=0, ge=0, le=10000)
    servings: int = Field(default=1, ge=1, le=100)
    ingredients: list[IngredientIn] = Field(min_length=1, max_length=200)
    steps: list[RecipeStepIn] = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        if len(value.strip()) < 3:
            raise ValueError("Title must contain at least 3 characters")
        return value.strip()

    @field_validator("image_url")
    @classmethod
    def valid_image(cls, value: str | None) -> str | None:
        return str(HttpUrl(value)) if value else None

    @model_validator(mode="after")
    def ordered_steps(self):
        if [step.step_number for step in self.steps] != list(range(1, len(self.steps) + 1)):
            raise ValueError("Steps must be ordered consecutively starting at 1")
        return self


# --- US1.4: Recipe Creation & Saving (Recipe Full Update Schema) ---
class RecipeUpdate(RecipeCreate):
    """PUT replaces the recipe, ingredients, and ordered steps."""


# --- US1.5: Personal Recipe Tab & Recipe Detail (Recipe Output Schema) ---
class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    author_username: str
    title: str
    description: str | None
    cuisine: str | None
    meal_type: str | None
    difficulty: str
    image_url: str | None
    prep_time_mins: int
    cook_time_mins: int
    servings: int
    ingredients: list[IngredientOut]
    steps: list[RecipeStepOut]
    created_at: datetime
    updated_at: datetime

# --- US2.2: Recipe Search & Discovery (Search Result Schemas) --
class RecipeSummaryOut(BaseModel):
    """Lightweight recipe summary returned in search grids and listing cards."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    author_username: str
    cuisine: str | None = None
    meal_type: str |None = None
    difficulty: str
    cook_time_mins: int
    image_url: str | None = None

class RecipeSearchResult(BaseModel):
    """Paginated search respinse w/ total hit count and current window"""
    total: int
    limit: int
    offset: int 
    items: list[RecipeSummaryOut]
