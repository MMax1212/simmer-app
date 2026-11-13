from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- US3.5 Task 3.5.1: User Follow Join Model ---
class UserFollow(Base):
    __tablename__ = "user_follows"
    __table_args__ = (
        CheckConstraint("follower_id != following_id", name="ck_user_follows_no_self_follow"),
    )

    follower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    following_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ORM Relationships
    follower: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[follower_id], back_populates="following_relations"
    )
    following: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[following_id], back_populates="follower_relations"
    )
