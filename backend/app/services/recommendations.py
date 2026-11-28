"""Deterministic preference matching for the US4.3.2 recommended endpoint."""
from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models import Recipe, Tag
from app.models.recipe import recipe_tags
from app.services.trending import (
    TrendingRecipe,
    read_discovery_rows,
    recipe_discovery_query,
    validate_discovery_page,
)


def normalize_preferences(values: list[str]) -> list[str]:
    """Match existing profile and hashtag spelling without inventing preferences."""
    normalized = {
        value.strip().lstrip("#").strip().lower().replace(" ", "-")
        for value in values
    }
    return sorted(value for value in normalized if value)


def _normalized_field(field: ColumnElement) -> ColumnElement:
    """Keep SQL normalization consistent with the stored profile normalization."""
    return func.replace(func.trim(func.ltrim(func.lower(func.trim(field)), "#")), " ", "-")


def recommend_recipes(
    db: Session, *, preferences: list[str], now: datetime, limit: int, offset: int,
) -> list[TrendingRecipe]:
    """Rank preference matches, or highest average cooking rating when none are set.

    Unrated recipes follow rated recipes; newest creation and ID break fallback
    ties. With no ratings at all, this naturally becomes a newest-recipes feed.
    Real preferences with no matches stay empty rather than showing unrelated food.
    """
    validate_discovery_page(now, limit, offset)
    statement = recipe_discovery_query(db, now=now)
    if not preferences:
        statement = statement.order_by(
            statement.selected_columns.average_rating.desc(),
            Recipe.created_at.desc(), Recipe.id.asc(),
        )
        return read_discovery_rows(db, statement.limit(limit).offset(offset))

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
        statement
        .where(match_count > 0)
        .order_by(
            match_count.desc(), statement.selected_columns.score.desc(),
            Recipe.created_at.desc(), Recipe.id.asc(),
        )
        .limit(limit)
        .offset(offset)
    )
    return read_discovery_rows(db, statement)
