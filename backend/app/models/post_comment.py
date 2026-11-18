from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- US3.3: Task 3.3.1: Post Comments Model ---
class PostComment(Base):
    """Stores discussion comments authored under community dish posts.

    Belongs to User Story 3.3 (Likes & Comments on Community Posts).
    Indexed by post_id and created_at for performant chronological thread queries.
    Cascade deletion cleans up comments if the parent post or commenting user is deleted.
    """

    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="post_comments")  # noqa: F821
    post: Mapped["Post"] = relationship(back_populates="comments")  # noqa: F821
