"""US4.3.2: named discovery routes precede the dynamic recipe-ID route."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.discovery import TrendingRecipeOut
from app.services.recommendations import normalize_preferences, recommend_recipes
from app.services.trending import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    TrendingRecipe,
    rank_trending_recipes,
)

router = APIRouter(prefix="/api/v1/recipes", tags=["discovery"])
PageLimit = Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)]
PageOffset = Annotated[int, Query(ge=0)]


def get_discovery_clock() -> datetime:
    """Inject a shared UTC clock so both feed contracts are testable over time."""
    return datetime.now(timezone.utc)


def _public_card(item: TrendingRecipe) -> TrendingRecipeOut:
    """Explicitly select public fields rather than serializing an ORM/user object."""
    recipe = item.recipe
    return TrendingRecipeOut(
        id=recipe.id, title=recipe.title, image_url=recipe.image_url,
        cuisine=recipe.cuisine, difficulty=recipe.difficulty,
        cook_time_mins=recipe.cook_time_mins, author_username=recipe.author_username,
        trending_score=item.score, likes_count=item.likes_count,
        completed_count=item.completed_count,
    )


@router.get("/trending", response_model=list[TrendingRecipeOut])
def get_trending_recipes(
    db: DbSession,
    now: Annotated[datetime, Depends(get_discovery_clock)],
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> list[TrendingRecipeOut]:
    """Return gravity-ranked cards, or top-rated/newest cards on global cold start."""
    ranked = rank_trending_recipes(db, now=now, limit=limit, offset=offset, include_fallback=True)
    return [_public_card(item) for item in ranked]


@router.get("/recommended", response_model=list[TrendingRecipeOut])
def get_recommended_recipes(
    user: CurrentUser,
    db: DbSession,
    now: Annotated[datetime, Depends(get_discovery_clock)],
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> list[TrendingRecipeOut]:
    """Use only the authenticated profile; empty preferences trigger rated fallback."""
    preferences = normalize_preferences(user.culinary_preferences or [])
    ranked = recommend_recipes(db, preferences=preferences, now=now, limit=limit, offset=offset)
    return [_public_card(item) for item in ranked]
