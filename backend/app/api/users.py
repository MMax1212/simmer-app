from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models import User
from app.schemas.user import ProfileUpdate, UserPrivate, UserPublic

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# --- US1.3: User Profile Management (Update Authenticated User Profile) ---
@router.put("/me", response_model=UserPrivate)
def update_me(body: ProfileUpdate, user: CurrentUser, db: DbSession):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# --- US1.3: User Profile Management (Public User Profile Lookup) ---
@router.get("/{username}", response_model=UserPublic)
def read_user(username: str, db: DbSession):
    user = db.scalar(select(User).where(func.lower(User.username) == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return user
