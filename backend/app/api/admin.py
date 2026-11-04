from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.api.deps import AdminUser, DbSession
from app.models import AdminAudit, Recipe, User
from app.schemas.admin import AdminStatsResponse
from app.schemas.user import AdminUserUpdate, UserPrivate

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# --- US1.2: Admin Account & RBAC (List All Registered Users with Optional Filtering) ---
@router.get("/users", response_model=list[UserPrivate])
def list_users(
    _: AdminUser,
    db: DbSession,
    role: str | None = Query(default=None, description="Filter by user role (user or admin)"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
):
    query = select(User).order_by(User.id)
    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    return db.scalars(query).all()


# --- US1.2: Admin Account & RBAC (Toggle User Active Status & Role with Audit Log) ---
@router.patch("/users/{user_id}/status", response_model=UserPrivate)
def update_user(user_id: int, body: AdminUserUpdate, admin: AdminUser, db: DbSession):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins can't change their own account here")
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Provide a status or role")
    before = {"role": user.role, "is_active": user.is_active}
    for field, value in changes.items():
        setattr(user, field, value)
    db.add(AdminAudit(admin_id=admin.id, target_id=user.id, before=before,
                      after={"role": user.role, "is_active": user.is_active}))
    db.commit()
    db.refresh(user)
    return user


# --- US1.2: Admin Account & RBAC (US-1.2-T-2: Admin Dashboard System Metrics) ---
@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(_: AdminUser, db: DbSession):
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
    deactivated_users = db.scalar(select(func.count(User.id)).where(User.is_active.is_(False))) or 0
    admin_users = db.scalar(select(func.count(User.id)).where(User.role == "admin")) or 0
    total_posts = db.scalar(select(func.count(Recipe.id))) or 0
    total_recipes = total_posts

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        deactivated_users=deactivated_users,
        admin_users=admin_users,
        total_posts=total_posts,
        total_recipes=total_recipes,
    )

