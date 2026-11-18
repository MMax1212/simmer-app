from datetime import datetime, timezone
from time import time
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

# --- US3.4.1 Saved post database entry---
class SavedPost(Base):
    __tablename__ = "saved_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column( ForeignKey("users.id", ondelete="CASCADE"), index=True )
    post_id: Mapped[int] = mapped_column( ForeignKey("posts.id", ondelete="CASCADE"), index=True )
    created_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, )

    __table_args__ = ( UniqueConstraint("user_id", "post_id", name="uq_saved_posts_user_post"), )

    #Relationships
    user: Mapped["User"] = relationship(back_populates="saved_posts") # noqa: F821
    post: Mapped["Post"] = relationship(back_populates="saved_by") # noqa: F821

