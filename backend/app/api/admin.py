from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import AdminUser, DbSession
from app.models import User
from app.schemas.user import AdminUserUpdate, UserPrivate

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserPrivate])
def list_users(_: AdminUser, db: DbSession):
    """US1.2: list all accounts."""
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/users/{user_id}", response_model=UserPrivate)
def update_user(user_id: int, body: AdminUserUpdate, admin: AdminUser, db: DbSession):
    """US1.2: deactivate/reactivate an account or change its role."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins can't change their own account here")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
