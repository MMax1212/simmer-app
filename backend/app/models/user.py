from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # --- US1.1: User Account Registration & Login ---
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    lates="owner", cascade="all, delete-orphan")  # noqa: F821

# --- US1.1: Unique Case-Insensitive Username Index ---
Index("uq_users_username_lower", func.lower(User.username), unique=True)
