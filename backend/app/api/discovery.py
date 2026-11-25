"""US4.3.2: recipe discovery routes, registered before /recipes/{recipe_id}."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.schemas.discovery import (
    RecommendedRecipePage,
    TrendingRecipePage,
    TrendingRecipeSummary,
)
from app.schemas.recipe import RecipeSummaryOut
from app.services.recommendations import normalize_preferences, recommend_recipes
from app.services.trending import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, rank_trending_recipes

router = APIRouter(prefix="/api/v1/recipes", tags=["discovery"])
PageLimit = Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)]
PageOffset = Annotated[int, Query(ge=0)]


def get_discovery_clock() -> datetime:
    """Provide an injectable UTC clock for deterministic API ranking tests."""
    return datetime.now(timezone.utc)


@router.get("/trending", response_model=TrendingRecipePage)
def get_trending_recipes(
    db: DbSession,
    now: Annotated[datetime, Depends(get_discovery_clock)],
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> TrendingRecipePage:
    """Return public recipe summaries ordered by configured recent engagement."""
    ranked = rank_trending_recipes(
        db, now=now, like_weight=settings.trending_like_weight,
        comment_weight=settings.trending_comment_weight,
        completion_weight=settings.trending_completion_weight,
        window_days=settings.trending_window_days,
        decay_hours=settings.trending_decay_hours, limit=limit, offset=offset,
    )
    # Explicit response models expose public card fields, never user credentials.
    items = [
        TrendingRecipeSummary(
            **RecipeSummaryOut.model_validate(item.recipe).model_dump(),
            score=item.score, likes_count=item.likes_count,
            comments_count=item.comments_count, completions_count=item.completions_count,
        )
        for item in ranked
    ]
    return TrendingRecipePage(limit=limit, offset=offset, items=items)


@router.get("/recommended", response_model=RecommendedRecipePage)
def get_recommended_recipes(
    user: CurrentUser,
    db: DbSession,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> RecommendedRecipePage:
    """Match the authenticated profile rather than caller-supplied user identifiers."""
    preferences = normalize_preferences(user.culinary_preferences or [])
    recipes = recommend_recipes(db, preferences=preferences, limit=limit, offset=offset)
    return RecommendedRecipePage(
        limit=limit, offset=offset, personalized=bool(preferences),
        items=[RecipeSummaryOut.model_validate(recipe) for recipe in recipes],
    )
