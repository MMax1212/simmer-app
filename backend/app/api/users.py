from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models import Recipe, User
from app.schemas.recipe import RecipeOut
from app.schemas.user import ProfileUpdate, UserPrivate, UserPublic

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserPrivate)
def read_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserPrivate)
def update_me(body: ProfileUpdate, user: CurrentUser, db: DbSession):
    """US1.3: edit bio, avatar URL, dietary preferences. Only fields you send are changed."""
    changes = body.model_dump(exclude_unset=True)
    if "dietary_prefs" in changes and changes["dietary_prefs"] is not None:
        changes["dietary_prefs"] = sorted({p.value for p in body.dietary_prefs or []})
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me/recipes", response_model=list[RecipeOut])
def my_recipes(user: CurrentUser, db: DbSession):
    """US1.5: the "My Recipes" tab, newest first."""
    return db.scalars(select(Recipe).where(Recipe.owner_id == user.id).order_by(Recipe.created_at.desc())).all()


@router.get("/{username}", response_model=UserPublic)
def read_user(username: str, db: DbSession):
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return user
