from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- US2.3: Mark & Log Completed Recipes (Cooking History Model) ---
class CompletedRecipe(Base):
    __tablename__ = "completed_recipes"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_completed_recipes_rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    cooked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="completed_recipes")  # noqa: F821
    recipe: Mapped["Recipe"] = relationship(back_populates="completed_logs")  # noqa: F821
