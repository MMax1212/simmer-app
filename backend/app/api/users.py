from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession, OptionalUser
from app.models import CompletedRecipe, Recipe, User, UserFollow
from app.schemas.recipe import CookingHistoryItemOut
from app.schemas.user import FollowToggleResponse, ProfileUpdate, UserPrivate, UserPublic

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _get_target_user(db: DbSession, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _get_follow_counts(db: DbSession, user_id: int) -> tuple[int, int]:
    followers_count = db.scalar(
        select(func.count(UserFollow.follower_id)).where(UserFollow.following_id == user_id)
    ) or 0
    following_count = db.scalar(
        select(func.count(UserFollow.following_id)).where(UserFollow.follower_id == user_id)
    ) or 0
    return followers_count, following_count


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


# --- US3.5 Task 3.5.2: Toggle Follow/Unfollow User Endpoint ---
@router.post("/{user_id}/follow", response_model=FollowToggleResponse)
def toggle_follow_user(user_id: int, user: CurrentUser, db: DbSession):
    target = _get_target_user(db, user_id)
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    existing = db.scalar(
        select(UserFollow).where(
            UserFollow.follower_id == user.id,
            UserFollow.following_id == target.id,
        )
    )
    if existing is not None:
        db.delete(existing)
        is_following = False
    else:
        new_follow = UserFollow(follower_id=user.id, following_id=target.id)
        db.add(new_follow)
        is_following = True

    db.commit()

    followers_count, following_count = _get_follow_counts(db, target.id)
    return FollowToggleResponse(
        following=is_following,
        followers_count=followers_count,
        following_count=following_count,
    )


# --- US3.5 Task 3.5.2: Get Follow Status & Follower Counts Endpoint ---
@router.get("/{user_id}/follow", response_model=FollowToggleResponse)
def get_follow_status(user_id: int, db: DbSession, current_user: OptionalUser = None):
    target = _get_target_user(db, user_id)
    followers_count, following_count = _get_follow_counts(db, target.id)

    is_following = False
    if current_user is not None:
        is_following = db.scalar(
            select(UserFollow).where(
                UserFollow.follower_id == current_user.id,
                UserFollow.following_id == target.id,
            )
        ) is not None

    return FollowToggleResponse(
        following=is_following,
        followers_count=followers_count,
        following_count=following_count,
    )


# --- US1.3: User Profile Management (Public User Profile Lookup) ---
@router.get("/{username}", response_model=UserPublic)
def read_user(username: str, db: DbSession):
    user = db.scalar(select(User).where(func.lower(User.username) == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return user
