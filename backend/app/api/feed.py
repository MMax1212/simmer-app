from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession, OptionalUser
from app.models import Post, UserFollow
from app.schemas.feed import FeedResponse

router = APIRouter(prefix="/api/v1/feed", tags=["feed"])


# --- US3.5 Task 3.5.3: Timeline Feed Endpoint (Fan-Out-On-Read) ---
@router.get("", response_model=FeedResponse)
def get_timeline_feed(
    db: DbSession,
    mode: str = Query(
        default="following",
        description="'following' to view followed creators, 'global' for all creators",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: OptionalUser = None,
):
    normalized_mode = mode.strip().lower()

    if normalized_mode == "following":
        # Following feed requires authentication
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for following feed",
            )

        # SPK-2.1 Fan-Out-On-Read: Relational subquery on user_follows
        following_subquery = (
            select(UserFollow.following_id)
            .where(UserFollow.follower_id == user.id)
        )

        query = (
            select(Post)
            .where(Post.author_id.in_(following_subquery))
            .options(selectinload(Post.author), selectinload(Post.recipe))
        )
        count_query = select(func.count(Post.id)).where(Post.author_id.in_(following_subquery))
        total = db.scalar(count_query) or 0

    else:
        # Global community feed: delivers all posts publicly
        query = (
            select(Post)
            .options(selectinload(Post.author), selectinload(Post.recipe))
        )
        count_query = select(func.count(Post.id))
        total = db.scalar(count_query) or 0

    # Reverse chronological sorting (newest first)
    query = (
        query.order_by(Post.created_at.desc(), Post.id.desc())
        .offset(offset)
        .limit(limit)
    )
    items = db.scalars(query).all()

    return FeedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )
