"""Deterministic preference matching for the US4.3.2 recommended endpoint."""
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.elements import ColumnElement

from app.models import Recipe, Tag
from app.models.recipe import recipe_tags


def normalize_preferences(values: list[str]) -> list[str]:
    """Match existing profile and hashtag spelling without inventing preferences."""
    normalized = {
        value.strip().lstrip("#").strip().lower().replace(" ", "-")
        for value in values
    }
    return sorted(value for value in normalized if value)


def _normalized_field(field: ColumnElement) -> ColumnElement:
    """Keep SQL normalization consistent with the stored profile normalization."""
    return func.replace(func.ltrim(func.lower(func.trim(field)), "#"), " ", "-")


def recommend_recipes(
    db: Session, *, preferences: list[str], limit: int, offset: int,
) -> list[Recipe]:
    """Rank exact normalized cuisine/meal/tag matches, then newest recipe and ID.

    This is a transparent initial matching rule, not nutritional verification or
    an allergy-safety guarantee. Cold-start/fallback presentation is a later task.
    Pagination is validated at the HTTP boundary before this service is called.
    """
    if not preferences:
        return []

    # A correlated count avoids duplicate recipe rows when several tags match.
    # DISTINCT prevents equivalent hashtag spellings from inflating the score.
    tag_matches = (
        select(func.count(func.distinct(_normalized_field(Tag.name))))
        .select_from(recipe_tags.join(Tag, Tag.id == recipe_tags.c.tag_id))
        .where(
            recipe_tags.c.recipe_id == Recipe.id,
            _normalized_field(Tag.name).in_(preferences),
        )
        .correlate(Recipe)
        .scalar_subquery()
    )
    match_count = (
        case((_normalized_field(Recipe.cuisine).in_(preferences), 1), else_=0)
        + case((_normalized_field(Recipe.meal_type).in_(preferences), 1), else_=0)
        + tag_matches
    )
    statement = (
        select(Recipe)
        .options(joinedload(Recipe.owner), joinedload(Recipe.tags))
        .where(match_count > 0)
        .order_by(match_count.desc(), Recipe.created_at.desc(), Recipe.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement).unique())
