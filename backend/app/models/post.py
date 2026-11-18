from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- US3.1: Community Food Posts (Core Post Model) ---
class Post(Base):
    """Represents a community social feed post sharing food photos, reviews, or tutorials.
    
    Belongs to User Story 3.1 (Publish Food Posts).
    Supports food photo uploads, video mukbangs/tutorials, optional recipe attachment,
    and automatic cascade cleanup.
    """
    __tablename__ = "posts"

    # Primary key identifier for the post
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign key referencing author user; cascade delete removes posts if user account is deleted
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Text description, cooking commentary, or recipe notes written by the author
    caption: Mapped[str] = mapped_column(Text)

    # Required media location string: supports external CDN links, local static uploads, or data URLs
    image_url: Mapped[str] = mapped_column(Text, nullable=False)

    # Media classifier: distinguishes standard photos from video reviews, mukbangs, or video tutorials
    media_type: Mapped[str] = mapped_column(String(20), default="image")  # "image" | "video"

    # Optional foreign key linking to a recipe. SET NULL ensures deleting a recipe preserves the post
    recipe_id: Mapped[int | None] = mapped_column(
        ForeignKey("recipes.id", ondelete="SET NULL"), index=True, default=None
    )

    # UTC timestamp for chronological feed ordering and engagement decay algorithms
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    # UTC timestamp tracking edits or updates to the post record
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Two-way SQLAlchemy ORM navigation
    # post.author provides direct access to the User who published this post
    author: Mapped["User"] = relationship(back_populates="posts")  # noqa: F821

    # post.recipe provides access to the linked Recipe entity (or None if post is standalone)
    recipe: Mapped["Recipe | None"] = relationship(back_populates="posts")  # noqa: F821
