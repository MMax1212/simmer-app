from datetime import datetime
from pydantic import BaseModel, ConfigDict


# --- US3.5 Task 3.5.3: Feed Post Author & Recipe Summary DTOs ---
class FeedPostAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    avatar_url: str | None = None


class FeedPostRecipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image_url: str | None = None
    cook_time_mins: int = 0
    difficulty: str | None = None


# --- US3.5 Task 3.5.3: Feed Post Output Schema ---
class FeedPostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    caption: str
    image_url: str
    media_type: str = "image"
    recipe_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    author: FeedPostAuthor | None = None
    recipe: FeedPostRecipe | None = None
    likes_count: int = 0
    comments_count: int = 0


# --- US3.5 Task 3.5.3: Paginated Feed Response Schema ---
class FeedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[FeedPostOut]
