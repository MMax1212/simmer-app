from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.deps import AdminUser, DbSession
from app.models import AdminAudit, User
from app.schemas.audit import AdminAuditResponse
from app.schemas.user import AdminUserUpdate, UserPrivate

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# --- US1.2: Admin Account & RBAC (List All Registered Users) ---
@router.get("/users", response_model=list[UserPrivate])
def list_users(_: AdminUser, db: DbSession):
    return db.scalars(select(User).order_by(User.id)).all()


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


# --- US1.2: Admin Account & RBAC (US-1.2-T-1: Inspect Audit Logs) ---
@router.get("/audit-logs", response_model=list[AdminAuditResponse])
def get_audit_logs(
    _: AdminUser,
    db: DbSession,
    target_id: int | None = Query(default=None, description="Filter by target user ID"),
    limit: int = Query(default=50, ge=1, le=100, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Records to skip"),
):
    query = select(AdminAudit).order_by(AdminAudit.created_at.desc(), AdminAudit.id.desc())
    if target_id is not None:
        query = query.where(AdminAudit.target_id == target_id)
    query = query.offset(offset).limit(limit)
    return db.scalars(query).all()

