from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- US3.3: Task 3.3.1: Post Likes Model ---
class PostLike(Base):
    """Tracks user likes on community posts with duplicate like prevention.

    Belongs to User Story 3.3 (Likes & Comments on Community Posts).
    Enforces UniqueConstraint on (user_id, post_id) so users can only like a post once.
    Cascade deletion cleans up likes if the target post or author user is deleted.
    """

    __tablename__ = "post_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_user_post_like"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="post_likes")  # noqa: F821
    post: Mapped["Post"] = relationship(back_populates="likes")  # noqa: F821
