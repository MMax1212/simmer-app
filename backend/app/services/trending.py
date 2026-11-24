"""Rank recipes from recent engagement without changing stored data.

Policy is explicit rather than a hidden product default. Each event contributes
weight / (1 + age_hours / decay_hours). At decay_hours old, an event contributes
half its original weight. The lookback window separately excludes stale events.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import isfinite

from sqlalchemy import DateTime, case, extract, func, literal, select, union_all
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.elements import ColumnElement

from app.models import CompletedRecipe, Post, PostComment, PostLike, Recipe

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
SECONDS_PER_HOUR = 3600.0
HOURS_PER_DAY = 24.0
LIKE_EVENT = "like"
COMMENT_EVENT = "comment"
COMPLETION_EVENT = "completion"


@dataclass(frozen=True)
class TrendingRecipe:
    """Ranked recipe with its decayed score and undecayed in-window event counts."""

    recipe: Recipe
    score: float
    likes_count: int
    comments_count: int
    completions_count: int


def _validate_policy(
    now: datetime,
    weights: tuple[float, float, float],
    window_days: int,
    decay_hours: float,
    limit: int,
    offset: int,
) -> None:
    """Reject invalid policy before constructing SQL or touching the database."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    for name, value, minimum in (
        ("window_days", window_days, 1), ("limit", limit, 1), ("offset", offset, 0),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if limit > MAX_PAGE_SIZE:
        raise ValueError(f"limit must not exceed {MAX_PAGE_SIZE}")
    if not isfinite(decay_hours) or decay_hours <= 0:
        raise ValueError("decay_hours must be finite and positive")
    if any(not isfinite(weight) or weight < 0 for weight in weights):
        raise ValueError("Engagement weights must be finite and nonnegative")


def _event_age_hours(
    occurred_at: ColumnElement, now: datetime, dialect_name: str,
) -> ColumnElement:
    """Express elapsed hours using each supported database's timestamp arithmetic."""
    clock = literal(now, type_=DateTime(timezone=True))
    if dialect_name == "sqlite":
        return (func.julianday(clock) - func.julianday(occurred_at)) * HOURS_PER_DAY
    if dialect_name == "postgresql":
        return extract("epoch", clock - occurred_at) / SECONDS_PER_HOUR
    raise NotImplementedError(f"Trending does not support database dialect {dialect_name}")


def rank_trending_recipes(
    db: Session,
    *,
    now: datetime,
    like_weight: float,
    comment_weight: float,
    completion_weight: float,
    window_days: int,
    decay_hours: float,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
) -> list[TrendingRecipe]:
    """Return positive-score recipes ordered by score, then ascending recipe ID.

    Args:
        db: Caller-owned session; the function never commits or modifies records.
        now: A timezone-aware clock, normalized to UTC for consistent comparison.
        like_weight: Contribution of a new like on a recipe-linked post.
        comment_weight: Contribution of a new comment on a recipe-linked post.
        completion_weight: Contribution of a new cooking completion; zero disables it.
        window_days: Inclusive recent-activity window; future events are excluded.
        decay_hours: Event age at which its contribution is halved.
        limit: Page size, from one to MAX_PAGE_SIZE.
        offset: Nonnegative number of ranked recipes to skip.

    Recipes without positive recent activity are excluded. Cold-start fallback
    belongs to Task 4.3.5. Counts describe all in-window events, even zero-weight
    signals; scores, not counts, determine inclusion and order.
    """
    _validate_policy(
        now, (like_weight, comment_weight, completion_weight),
        window_days, decay_hours, limit, offset,
    )
    now = now.astimezone(timezone.utc)
    cutoff = now - timedelta(days=window_days)

    # Likes and comments belong to posts, not directly to recipes. UNION ALL keeps
    # one row per event; joining all engagement tables would multiply their counts.
    # Multiple posts may contribute to one recipe; unlinked posts contribute nothing.
    events = union_all(
        select(
            Post.recipe_id.label("recipe_id"), PostLike.created_at.label("occurred_at"),
            literal(like_weight).label("weight"), literal(LIKE_EVENT).label("kind"),
        ).join(Post, Post.id == PostLike.post_id).where(Post.recipe_id.is_not(None)),
        select(
            Post.recipe_id.label("recipe_id"), PostComment.created_at.label("occurred_at"),
            literal(comment_weight).label("weight"), literal(COMMENT_EVENT).label("kind"),
        ).join(Post, Post.id == PostComment.post_id).where(Post.recipe_id.is_not(None)),
        select(
            CompletedRecipe.recipe_id.label("recipe_id"),
            CompletedRecipe.cooked_at.label("occurred_at"),
            literal(completion_weight).label("weight"),
            literal(COMPLETION_EVENT).label("kind"),
        ),
    ).subquery("recipe_engagement_events")

    age_hours = _event_age_hours(events.c.occurred_at, now, db.get_bind().dialect.name)
    contribution = events.c.weight / (1.0 + age_hours / decay_hours)
    metrics = (
        select(
            events.c.recipe_id,
            func.sum(contribution).label("score"),
            func.sum(case((events.c.kind == LIKE_EVENT, 1), else_=0)).label("likes_count"),
            func.sum(case((events.c.kind == COMMENT_EVENT, 1), else_=0)).label("comments_count"),
            func.sum(case((events.c.kind == COMPLETION_EVENT, 1), else_=0)).label(
                "completions_count"
            ),
        )
        .where(events.c.occurred_at >= cutoff, events.c.occurred_at <= now)
        .group_by(events.c.recipe_id)
        .subquery("recipe_engagement_metrics")
    )

    # Rank and paginate in SQL, not by fetching all recipes into Python. The ID
    # tie-breaker makes equal-score pages deterministic for the same clock/data.
    statement = (
        select(
            Recipe, metrics.c.score, metrics.c.likes_count,
            metrics.c.comments_count, metrics.c.completions_count,
        )
        # Recipe.tags normally uses select-in loading (a second query). Join the
        # display metadata here; SQLAlchemy paginates recipes before eager joins.
        .options(joinedload(Recipe.tags), joinedload(Recipe.owner))
        .join(metrics, metrics.c.recipe_id == Recipe.id)
        .where(metrics.c.score > 0)
        .order_by(metrics.c.score.desc(), Recipe.id.asc())
        .limit(limit)
        .offset(offset)
    )
    return [
        TrendingRecipe(
            recipe=row[0], score=float(row[1]), likes_count=int(row[2]),
            comments_count=int(row[3]), completions_count=int(row[4]),
        )
        for row in db.execute(statement).unique()
    ]
