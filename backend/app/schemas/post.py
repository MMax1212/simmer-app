from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


# US3.2.1: PUT reuses creation fields, but never accepts author or timestamp changes.
class PostUpdate(PostCreate):
    """Full replacement of editable fields; omitted optional fields use their defaults."""

    @field_validator("caption", "image_url")
    @classmethod
    def reject_blank_content(cls, value: str) -> str:
        # Preserve formatting and media strings verbatim; reject whitespace-only content.
        if not value.strip():
            raise ValueError("Must not be blank")
        return value
