"""SQL-backed discovery metrics and the Sprint 4 recipe-age gravity formula."""
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime, Integer, Select, case, cast, exists, extract, func, literal, select, union_all,
)
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.elements import ColumnElement

from app.models import CompletedRecipe, Post, PostComment, PostLike, Recipe

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 20
SECONDS_PER_HOUR = 3600.0
HOURS_PER_DAY = 24.0
LIKE_WEIGHT = 2
COMMENT_WEIGHT = 3
COMPLETION_WEIGHT = 5
GRAVITY_OFFSET_HOURS = 2.0
GRAVITY_EXPONENT = 1.5
LIKE_EVENT = "like"
COMMENT_EVENT = "comment"
COMPLETION_EVENT = "completion"


@dataclass(frozen=True)
class TrendingRecipe:
    """Public-card source plus independently aggregated engagement metrics."""

    recipe: Recipe
    score: float
    likes_count: int
    comments_count: int
    completed_count: int


def validate_discovery_page(now: datetime, limit: int, offset: int) -> None:
    """Validate internal callers as well as FastAPI's HTTP query boundary."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    for name, value, minimum in (("limit", limit, 1), ("offset", offset, 0)):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if limit > MAX_PAGE_SIZE:
        raise ValueError(f"limit must not exceed {MAX_PAGE_SIZE}")


def _recipe_age_hours(now: datetime, dialect_name: str) -> ColumnElement:
    """Use recipe creation, rather than engagement time, as the gravity clock."""
    clock = literal(now, type_=DateTime(timezone=True))
    if dialect_name == "sqlite":
        return (func.julianday(clock) - func.julianday(Recipe.created_at)) * HOURS_PER_DAY
    if dialect_name == "postgresql":
        return extract("epoch", clock - Recipe.created_at) / SECONDS_PER_HOUR
    raise NotImplementedError(f"Discovery does not support database dialect {dialect_name}")


def recipe_discovery_query(db: Session, *, now: datetime) -> Select:
    """Build reusable metrics for trending, preference matches, and rated fallback.

    All engagement through the supplied clock counts: the specified formula has
    no lookback cutoff. Future events and future-dated recipes are excluded.
    Aggregation precedes metadata joins and pagination, preventing inflated counts.
    """
    now = now.astimezone(timezone.utc)
    # UNION ALL preserves one row per event, including multiple posts per recipe.
    # Only completion rows carry a rating, so AVG ignores likes and comments.
    # Typed NULLs keep PostgreSQL from resolving the first UNION arms to text.
    no_rating = cast(literal(None), Integer)
    events = union_all(
        select(
            Post.recipe_id.label("recipe_id"), PostLike.created_at.label("occurred_at"),
            literal(LIKE_EVENT).label("kind"), no_rating.label("rating"),
        ).join(Post, Post.id == PostLike.post_id).where(Post.recipe_id.is_not(None)),
        select(
            Post.recipe_id.label("recipe_id"), PostComment.created_at.label("occurred_at"),
            literal(COMMENT_EVENT).label("kind"), no_rating.label("rating"),
        ).join(Post, Post.id == PostComment.post_id).where(Post.recipe_id.is_not(None)),
        select(
            CompletedRecipe.recipe_id, CompletedRecipe.cooked_at,
            literal(COMPLETION_EVENT), CompletedRecipe.rating,
        ),
    ).subquery("recipe_engagement_events")
    metrics = (
        select(
            events.c.recipe_id,
            func.sum(case((events.c.kind == LIKE_EVENT, 1), else_=0)).label("likes_count"),
            func.sum(case((events.c.kind == COMMENT_EVENT, 1), else_=0)).label("comments_count"),
            func.sum(case((events.c.kind == COMPLETION_EVENT, 1), else_=0)).label(
                "completed_count"
            ),
            func.avg(events.c.rating).label("average_rating"),
        )
        .where(events.c.occurred_at <= now)
        .group_by(events.c.recipe_id)
        .subquery("recipe_engagement_metrics")
    )
    likes = func.coalesce(metrics.c.likes_count, 0)
    comments = func.coalesce(metrics.c.comments_count, 0)
    completed = func.coalesce(metrics.c.completed_count, 0)
    weighted_count = likes * LIKE_WEIGHT + comments * COMMENT_WEIGHT + completed * COMPLETION_WEIGHT
    age = _recipe_age_hours(now, db.get_bind().dialect.name)
    score = weighted_count / func.pow(age + GRAVITY_OFFSET_HOURS, GRAVITY_EXPONENT)
    return (
        select(
            Recipe, score.label("score"), likes.label("likes_count"),
            comments.label("comments_count"), completed.label("completed_count"),
            func.coalesce(metrics.c.average_rating, 0).label("average_rating"),
        )
        .options(joinedload(Recipe.owner), joinedload(Recipe.tags))
        .outerjoin(metrics, metrics.c.recipe_id == Recipe.id)
        .where(Recipe.created_at <= now)
    )


def read_discovery_rows(db: Session, statement: Select) -> list[TrendingRecipe]:
    """Collapse eager tag joins without duplicating recipes in the returned page."""
    return [
        TrendingRecipe(
            recipe=row[0], score=float(row[1]), likes_count=int(row[2]),
            comments_count=int(row[3]), completed_count=int(row[4]),
        )
        for row in db.execute(statement).unique()
    ]


def rank_trending_recipes(
    db: Session, *, now: datetime, limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0, include_fallback: bool = False,
) -> list[TrendingRecipe]:
    """Rank by gravity, optionally falling back only when no recipe has engagement.

    The existence check applies to the whole ranking, before pagination. An empty
    later page therefore stays empty instead of unexpectedly switching to fallback.
    Equal scores use ascending recipe IDs for deterministic pagination.
    """
    validate_discovery_page(now, limit, offset)
    statement = recipe_discovery_query(db, now=now)
    score = statement.selected_columns.score
    rating = statement.selected_columns.average_rating
    if include_fallback:
        # A separate SQL subquery (not an extra round trip) checks global cold start.
        ranked = statement.with_only_columns(Recipe.id).where(score > 0).subquery()
        has_engagement = exists(select(ranked.c.id))
        statement = statement.where((score > 0) | ~has_engagement).order_by(
            score.desc(),
            case((~has_engagement, rating), else_=0).desc(),
            case((~has_engagement, Recipe.created_at), else_=None).desc(),
            Recipe.id.asc(),
        )
    else:
        statement = statement.where(score > 0).order_by(score.desc(), Recipe.id.asc())
    return read_discovery_rows(db, statement.limit(limit).offset(offset))
