from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models import Post, PostLike, Recipe, SavedPost
from app.schemas.post import LikeToggleResponse, PostCreate, PostResponse, PostUpdate

# Route prefix for all community post endpoints: /api/v1/posts
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


def _to_post_response(post: Post) -> PostResponse:
    """Helper to convert a Post ORM database entity into a client-facing PostResponse DTO.

    Extracts author username and optional recipe title so clients don't need
    secondary round-trips to render author and recipe chips.
    """
    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        author_username=post.author.username if post.author else "",
        caption=post.caption,
        image_url=post.image_url,
        media_type=post.media_type,
        recipe_id=post.recipe_id,
        recipe_title=post.recipe.title if post.recipe else None,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


# --- US3.1: Task 3.1.2: Create a Community Food Post ---
@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(body: PostCreate, user: CurrentUser, db: DbSession):
    """Publish a new dish post to the community feed.

    1. Requires authentication (CurrentUser guard returns 401 if token is missing/invalid).
    2. Validates optional recipe_id: if supplied, verifies the recipe exists in DB (returns 404 if not found).
    3. Persists the new Post entity with author_id set to the authenticated user's ID.
    4. Returns HTTP 201 Created with the serialized post and author metadata.
    """
    # Relational integrity check: if recipe_id is provided, verify it points to a valid recipe
    if body.recipe_id is not None:
        recipe = db.get(Recipe, body.recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Linked recipe not found")

    # Instantiate the Post ORM model with validated payload values
    new_post = Post(
        author_id=user.id,
        caption=body.caption,
        image_url=body.image_url,
        media_type=body.media_type,
        recipe_id=body.recipe_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return _to_post_response(new_post)


# --- US3.1: Task 3.1.2: Get Post by ID ---
@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: DbSession):
    """Retrieve full details of a specific community post by its unique ID.

    1. Public endpoint (no login required so shared links are viewable).
    2. Uses selectinload on author and recipe to eagerly fetch joined metadata in a single query.
    3. Returns HTTP 404 Not Found if post_id does not exist.
    """
    query = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.recipe))
        .where(Post.id == post_id)
    )
    post = db.scalar(query)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return _to_post_response(post)


# --- US3.2.1: Shared lookup and authorization for post lifecycle changes ---
def _require_post_author(post_id: int, user: CurrentUser, db: DbSession) -> Post:
    """Return an existing author-owned post, or reject the write before mutation."""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    # This story is author-only: unlike recipe management, it has no admin override.
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="You can only change your own posts")
    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, body: PostUpdate, user: CurrentUser, db: DbSession):
    """Replace editable post content while preserving authorship and creation time."""
    post = _require_post_author(post_id, user, db)
    # Validate the association before touching persistent fields so a failed lookup
    # cannot leave an otherwise partially modified post in the current transaction.
    recipe = None
    if body.recipe_id is not None:
        recipe = db.get(Recipe, body.recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Linked recipe not found")

    post.caption = body.caption
    post.image_url = body.image_url
    post.media_type = body.media_type
    # Assign the relationship as well as its FK: serialization must see the new
    # recipe title even if the previous relationship was already loaded in session.
    post.recipe = recipe
    post.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(post)
    return _to_post_response(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, user: CurrentUser, db: DbSession):
    """Delete an author's post and its owned engagement records, never its recipe."""
    post = _require_post_author(post_id, user, db)
    # Existing ORM delete-orphan and database CASCADE rules remove likes, comments,
    # and saved-post references. A post references its recipe; it does not own it.
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- US3.3.2: Task 3.3.2: Toggle Post Like ---
@router.post("/{post_id}/like", response_model=LikeToggleResponse, status_code=status.HTTP_200_OK)
def toggle_post_like(post_id: int, user: CurrentUser, db: DbSession):
    """Toggle the current user's like on a community post.

    1. Requires authentication via CurrentUser dependency (returns 401 if unauthenticated).
    2. Validates post existence (returns 404 if post does not exist).
    3. If the user already liked the post, deletes the like record (unlikes).
    4. If the user has not liked the post, inserts a new PostLike record (likes).
    5. Returns LikeToggleResponse with updated boolean `liked` status and total `likes_count`.
    """
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = db.execute(
        select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == user.id)
    ).scalar_one_or_none()

    if existing_like:
        db.delete(existing_like)
        liked = False
    else:
        new_like = PostLike(user_id=user.id, post_id=post_id)
        db.add(new_like)
        liked = True

    db.commit()

    likes_count = db.scalar(
        select(func.count(PostLike.id)).where(PostLike.post_id == post_id)
    ) or 0

    return LikeToggleResponse(liked=liked, likes_count=likes_count)
