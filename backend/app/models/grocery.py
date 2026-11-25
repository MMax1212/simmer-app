"""Database models for grocery checklists and checklist items (US4.2 / Task 4.2.2).

Provides the relational persistence foundation for multi-recipe grocery checklist
generation, aisle sorting, and shopping completion tracking.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.user import User

DEFAULT_GROCERY_TITLE: str = "My Grocery List"
DEFAULT_DEPARTMENT: str = "Other"
MAX_TITLE_LENGTH: int = 100
MAX_NAME_LENGTH: int = 100
MAX_UNIT_LENGTH: int = 30
MAX_DEPARTMENT_LENGTH: int = 50


class GroceryList(Base):
    """Represents a user-owned shopping checklist."""

    __tablename__ = "grocery_lists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(MAX_TITLE_LENGTH),
        nullable=False,
        default=DEFAULT_GROCERY_TITLE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="grocery_lists")
    items: Mapped[list["GroceryItem"]] = relationship(
        "GroceryItem",
        back_populates="grocery_list",
        cascade="all, delete-orphan",
        order_by="GroceryItem.id",
    )


class GroceryItem(Base):
    """Represents an individual ingredient item on a grocery checklist."""

    __tablename__ = "grocery_items"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_grocery_items_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    grocery_list_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grocery_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(MAX_NAME_LENGTH),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(MAX_UNIT_LENGTH), nullable=False)
    department: Mapped[str] = mapped_column(
        String(MAX_DEPARTMENT_LENGTH),
        nullable=False,
        default=DEFAULT_DEPARTMENT,
        index=True,
    )
    is_checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_recipe_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("recipes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    grocery_list: Mapped["GroceryList"] = relationship(
        "GroceryList", back_populates="items"
    )
    source_recipe: Mapped["Recipe | None"] = relationship(
        "Recipe", back_populates="grocery_items"
    )
