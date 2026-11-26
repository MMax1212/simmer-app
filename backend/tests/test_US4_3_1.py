"""Gravity ranking regressions use a fixed clock and independently computed scores."""
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models import CompletedRecipe, Post, PostComment, PostLike, Recipe, Tag, User
from app.services.trending import rank_trending_recipes

NOW = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)


@pytest.fixture()
def ranking_data(db_session: Session) -> tuple[User, Callable]:
    """Build independent recipes and posts so count multiplication is observable."""
    user = User(email="rank@example.com", username="ranker", hashed_password="test-only")
    db_session.add(user)
    db_session.flush()

    def create_recipe(title: str, age_hours: float = 0) -> tuple[Recipe, Post]:
        recipe = Recipe(
            author_id=user.id, title=title, created_at=NOW - timedelta(hours=age_hours),
        )
        db_session.add(recipe)
        db_session.flush()
        post = Post(author_id=user.id, recipe_id=recipe.id, caption=title, image_url="/t.jpg")
        db_session.add(post)
        db_session.flush()
        return recipe, post

    return user, create_recipe


def rank(db: Session, **overrides):
    return rank_trending_recipes(db, **{"now": NOW, **overrides})


def test_empty_database_has_no_trending_recipes(db_session):
    assert rank(db_session) == []


def test_each_signal_counts_once_in_specified_gravity_formula(db_session, ranking_data):
    user, create = ranking_data
    recipe, post = create("Dinner", age_hours=2)
    db_session.add_all([
        PostLike(user_id=user.id, post_id=post.id, created_at=NOW),
        PostComment(user_id=user.id, post_id=post.id, content="First", created_at=NOW),
        PostComment(user_id=user.id, post_id=post.id, content="Second", created_at=NOW),
        CompletedRecipe(user_id=user.id, recipe_id=recipe.id, cooked_at=NOW),
    ])
    db_session.flush()
    item = rank(db_session)[0]
    assert item.recipe.id == recipe.id
    assert item.score == pytest.approx((2 + 2 * 3 + 5) / (2 + 2) ** 1.5)
    assert (item.likes_count, item.comments_count, item.completed_count) == (1, 2, 1)


def test_recipe_age_controls_decay_not_event_age(db_session, ranking_data):
    user, create = ranking_data
    older, old_post = create("Older", age_hours=24)
    recent, new_post = create("Recent", age_hours=2)
    db_session.add_all([
        PostLike(user_id=user.id, post_id=old_post.id, created_at=NOW),
        PostLike(user_id=user.id, post_id=new_post.id, created_at=NOW - timedelta(hours=1)),
    ])
    db_session.flush()
    items = rank(db_session)
    assert [item.recipe.id for item in items] == [recent.id, older.id]
    assert [item.score for item in items] == pytest.approx([2 / 4 ** 1.5, 2 / 26 ** 1.5])
    later = rank(db_session, now=NOW + timedelta(hours=2))
    assert later[0].score == pytest.approx(2 / 6 ** 1.5)


def test_old_engagement_counts_but_future_activity_and_recipes_do_not(db_session, ranking_data):
    user, create = ranking_data
    recipe, post = create("Old but active", age_hours=1000)
    future, future_post = create("Future recipe", age_hours=-1)
    db_session.add_all([
        PostLike(user_id=user.id, post_id=post.id, created_at=NOW - timedelta(days=30)),
        PostComment(user_id=user.id, post_id=post.id, content="Future",
                    created_at=NOW + timedelta(seconds=1)),
        CompletedRecipe(user_id=user.id, recipe_id=future.id, cooked_at=NOW),
        PostLike(user_id=user.id, post_id=future_post.id, created_at=NOW),
    ])
    db_session.flush()
    items = rank(db_session)
    assert len(items) == 1 and items[0].recipe.id == recipe.id
    assert items[0].score == pytest.approx(2 / 1002 ** 1.5)
    assert items[0].comments_count == 0


def test_multiple_posts_aggregate_and_unlinked_posts_are_ignored(db_session, ranking_data):
    user, create = ranking_data
    recipe, first = create("Shared")
    second = Post(author_id=user.id, recipe_id=recipe.id, caption="Again", image_url="/t.jpg")
    unlinked = Post(author_id=user.id, caption="Unlinked", image_url="/t.jpg")
    db_session.add_all([second, unlinked])
    db_session.flush()
    for post in [first, second, unlinked]:
        db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.flush()
    items = rank(db_session)
    assert len(items) == 1 and items[0].recipe.id == recipe.id
    assert items[0].score == pytest.approx(4 / 2 ** 1.5)


def test_equal_score_pages_are_stable_and_exclude_unengaged_recipes(db_session, ranking_data):
    user, create = ranking_data
    recipes = []
    for title in ["One", "Two", "Three"]:
        recipe, post = create(title)
        recipes.append(recipe)
        db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    create("No activity")
    db_session.flush()
    assert [item.recipe.id for item in rank(db_session, limit=2)] == [r.id for r in recipes[:2]]
    assert [item.recipe.id for item in rank(db_session, limit=2, offset=2)] == [recipes[2].id]
    assert rank(db_session, offset=100) == []


@pytest.mark.parametrize("overrides", [
    {"limit": 0}, {"limit": 21}, {"limit": True}, {"offset": -1},
    {"offset": 0.5}, {"now": NOW.replace(tzinfo=None)},
])
def test_invalid_pagination_or_clock_is_rejected(db_session, overrides):
    with pytest.raises(ValueError):
        rank(db_session, **overrides)


def test_utc_offset_clock_represents_same_instant(db_session, ranking_data):
    user, create = ranking_data
    _, post = create("Same instant")
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.flush()
    local_clock = NOW.astimezone(timezone(timedelta(hours=-8)))
    assert rank(db_session, now=local_clock)[0].score == pytest.approx(rank(db_session)[0].score)


def test_ranking_is_one_read_query_even_with_multiple_tags(db_session, ranking_data):
    user, create = ranking_data
    recipe, post = create("Read-only")
    recipe.tags = [Tag(name="#quick"), Tag(name="#dinner")]
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.commit()
    statements = []

    def record_query(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    engine = db_session.get_bind()
    event.listen(engine, "before_cursor_execute", record_query)
    try:
        assert len(rank(db_session)) == 1
    finally:
        event.remove(engine, "before_cursor_execute", record_query)
    assert len(statements) == 1 and statements[0].lstrip().upper().startswith("SELECT")
    assert not db_session.new and not db_session.dirty and not db_session.deleted
