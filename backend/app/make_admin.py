"""Promote an existing account to admin.

Usage (from backend/, venv active):  python -m app.make_admin you@example.com
"""
import sys

from sqlalchemy import select

from app import models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.models import User


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m app.make_admin <email>")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == sys.argv[1].lower()))
        if user is None:
            sys.exit(f"No user with email {sys.argv[1]}. Register first.")
        user.role = "admin"
        db.commit()
        print(f"{user.username} is now an admin.")


if __name__ == "__main__":
    main()
