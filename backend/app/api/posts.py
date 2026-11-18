from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models import Post, SavedPost

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


# --- US3.4 Task 3.4.2: Bookmark / Unbookmark Toggle Endpoint ---
@router.post("/{post_id}/bookmark")
def toggle_bookmark(post_id: int, user: CurrentUser, db: DbSession):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = db.scalar(
        select(SavedPost).where(
            SavedPost.user_id == user.id,
            SavedPost.post_id == post_id,
        )
    )

    if existing:
        db.delete(existing)
        db.commit()
        return {"bookmark": False, "bookmarked": False}

    saved = SavedPost(user_id=user.id, post_id=post_id)
    db.add(saved)
    db.commit()
    return {"bookmark": True, "bookmarked": True}
