from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# --- US3.1: Post Creation Request DTO ---
class PostCreate(BaseModel):
    """Pydantic validation schema for incoming post creation payloads (POST /api/v1/posts).
    
    Disallows unrecognized fields (extra="forbid") and enforces non-empty
    caption and media URLs.
    """
    model_config = ConfigDict(extra="forbid")

    # Author's commentary, review notes, or cooking tips
    caption: str = Field(min_length=1, max_length=2000, description="Description or commentary for the post")

    # Required location of the media: URL, local path, or base64 data string
    image_url: str = Field(min_length=1, max_length=1000, description="URL or location of the food photo or video")

    # Content format: distinguishes standard photos from review videos, mukbangs, or tutorials
    media_type: Literal["image", "video"] = "image"

    # Optional foreign key linking to one of the user's recipes
    recipe_id: int | None = Field(default=None, description="Optional ID of an attached recipe")


# --- US3.1: Post Response DTO ---
class PostResponse(BaseModel):
    """Standardized response schema returned to clients when retrieving or creating a post."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    author_username: str
    caption: str
    image_url: str
    media_type: str
    recipe_id: int | None
    recipe_title: str | None
    created_at: datetime
    updated_at: datetime


# --- US3.3.2: Like Toggle Response DTO ---
class LikeToggleResponse(BaseModel):
    """Schema returned after toggling a like on a post."""
    liked: bool = Field(description="Whether the calling user currently likes the post after the toggle")
    likes_count: int = Field(ge=0, description="Total number of likes on the post after the toggle")

