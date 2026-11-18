from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models import Post, Recipe
from app.schemas.post import PostCreate, PostResponse

# Route prefix for all community post endpoints: /api/v1/posts
router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


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
