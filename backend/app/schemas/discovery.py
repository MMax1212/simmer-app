"""The shared list-item contract specified for both discovery endpoints."""
from pydantic import BaseModel, ConfigDict, Field


class TrendingRecipeOut(BaseModel):
    """Expose only public card fields and the agreed engagement metrics."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image_url: str | None = None
    cuisine: str | None = None
    difficulty: str
    cook_time_mins: int
    author_username: str
    trending_score: float = Field(ge=0, allow_inf_nan=False)
    likes_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
