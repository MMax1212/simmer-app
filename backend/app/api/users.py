from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models import CompletedRecipe, Recipe, User, SavedPost, Post
from app.schemas.recipe import CookingHistoryItemOut
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


# --- US2.3 Task 2.3.2: Get User's Cooking History Endpoint ---
# Placed before /{username} so "me" is not captured as a username path param
@router.get("/me/cooking-history", response_model=list[CookingHistoryItemOut])
def get_my_cooking_history(user: CurrentUser, db: DbSession):
    query = (
        select(
            CompletedRecipe.id,
            CompletedRecipe.recipe_id,
            Recipe.title.label("recipe_title"),
            Recipe.image_url.label("recipe_image_url"),
            CompletedRecipe.cooked_at,
            CompletedRecipe.notes,
            CompletedRecipe.rating,
        )
        .join(Recipe, CompletedRecipe.recipe_id == Recipe.id)
        .where(CompletedRecipe.user_id == user.id)
        .order_by(CompletedRecipe.cooked_at.desc(), CompletedRecipe.id.desc())
    )
    rows = db.execute(query).mappings().all()
    return [CookingHistoryItemOut(**row) for row in rows]


# --- US1.3: User Profile Management (Public User Profile Lookup) ---
@router.get("/{username}", response_model=UserPublic)
def read_user(username: str, db: DbSession):
    user = db.scalar(select(User).where(func.lower(User.username) == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- US3.4 Task 3.4.2: Get User's Saved / Bookmarked Posts ---
@router.get("/me/saved-posts")
def get_my_saved_posts(user: CurrentUser, db: DbSession):
    query = (
        select(Post)
        .join(SavedPost, SavedPost.post_id == Post.id)
        .where(SavedPost.user_id == user.id)
        .order_by(SavedPost.created_at.desc())
    )
    posts = db.scalars(query).all()
    return [
        {
            "id": p.id,
            "author_id": p.author_id,
            "caption": p.caption,
            "image_url": p.image_url,
            "media_type": p.media_type,
            "recipe_id": p.recipe_id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in posts
    ]
