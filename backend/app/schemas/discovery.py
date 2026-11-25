"""Public response contracts for US4.3 recipe discovery."""
from pydantic import BaseModel, Field

from app.schemas.recipe import RecipeSummaryOut


class TrendingRecipeSummary(RecipeSummaryOut):
    """Recipe-card fields plus auditable in-window engagement metrics."""

    score: float = Field(ge=0)
    likes_count: int = Field(ge=0)
    comments_count: int = Field(ge=0)
    completions_count: int = Field(ge=0)


class TrendingRecipePage(BaseModel):
    """Bounded ranking page; no misleading total inferred from page length."""

    limit: int
    offset: int
    items: list[TrendingRecipeSummary]


class RecommendedRecipePage(BaseModel):
    """Personalized indicates usable preferences, not a guarantee of matches."""

    limit: int
    offset: int
    personalized: bool
    items: list[RecipeSummaryOut]
