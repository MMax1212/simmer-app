"""Recipe-ranking behavior with explicit weights and a fixed UTC clock."""
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from app.models import CompletedRecipe, Post, PostComment, PostLike, Recipe, Tag, User
from app.services.trending import rank_trending_recipes

NOW = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)
# Test inputs demonstrate the formula; they are not approved product defaults.
POLICY = {
    "like_weight": 3.0,
    "comment_weight": 5.0,
    "completion_weight": 4.0,
    "window_days": 7,
    "decay_hours": 24.0,
}


@pytest.fixture()
def ranking_data(db_session: Session) -> tuple[User, Callable[[str], tuple[Recipe, Post]]]:
    """Create recipe-linked posts without repeating unrelated authentication tests."""
    user = User(email="rank@example.com", username="ranker", hashed_password="test-only")
    db_session.add(user)
    db_session.flush()

    def create_recipe(title: str) -> tuple[Recipe, Post]:
        recipe = Recipe(author_id=user.id, title=title, created_at=NOW - timedelta(days=90))
        db_session.add(recipe)
        db_session.flush()
        post = Post(
            author_id=user.id, recipe_id=recipe.id, caption=title,
            image_url="/test.jpg", created_at=NOW,
        )
        db_session.add(post)
        db_session.flush()
        return recipe, post

    return user, create_recipe


def rank(db: Session, **overrides):
    """Use an explicit policy so future configuration changes cannot destabilize tests."""
    return rank_trending_recipes(db, now=NOW, **{**POLICY, **overrides})


def test_empty_database_has_no_trending_recipes(db_session):
    assert rank(db_session) == []


def test_each_engagement_counts_once_without_join_multiplication(db_session, ranking_data):
    user, create = ranking_data
    recipe, post = create("Dinner")
    db_session.add_all([
        PostLike(user_id=user.id, post_id=post.id, created_at=NOW),
        PostComment(user_id=user.id, post_id=post.id, content="First", created_at=NOW),
        PostComment(user_id=user.id, post_id=post.id, content="Second", created_at=NOW),
        CompletedRecipe(user_id=user.id, recipe_id=recipe.id, cooked_at=NOW),
    ])
    db_session.flush()
    item = rank(db_session)[0]
    assert item.recipe.id == recipe.id
    assert item.score == pytest.approx(17.0)  # 3 + 2*5 + 4, not a multiplied join.
    assert (item.likes_count, item.comments_count, item.completions_count) == (1, 2, 1)


def test_recent_activity_outranks_old_activity_even_on_old_recipes(db_session, ranking_data):
    user, create = ranking_data
    older, old_post = create("Older")
    recent, new_post = create("Recent")
    db_session.add_all([
        PostLike(user_id=user.id, post_id=old_post.id, created_at=NOW - timedelta(hours=24)),
        PostLike(user_id=user.id, post_id=new_post.id, created_at=NOW),
    ])
    db_session.flush()
    items = rank(db_session)
    assert [item.recipe.id for item in items] == [recent.id, older.id]
    assert [item.score for item in items] == pytest.approx([3.0, 1.5])


def test_decay_applies_to_comments_and_completions(db_session, ranking_data):
    user, create = ranking_data
    _, post = create("Older signals")
    db_session.add_all([
        PostComment(user_id=user.id, post_id=post.id, content="Nice",
                    created_at=NOW - timedelta(hours=24)),
        CompletedRecipe(user_id=user.id, recipe_id=post.recipe_id,
                        cooked_at=NOW - timedelta(hours=24)),
    ])
    db_session.flush()
    assert rank(db_session)[0].score == pytest.approx(4.5)


def test_window_excludes_stale_and_future_events(db_session, ranking_data):
    user, create = ranking_data
    for title, delta in [
        ("Stale", -timedelta(days=7, seconds=1)),
        ("Future", timedelta(seconds=1)),
        ("Cutoff", -timedelta(days=7)),
    ]:
        recipe, post = create(title)
        db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW + delta))
    db_session.flush()
    assert [item.recipe.id for item in rank(db_session)] == [recipe.id]


def test_multiple_posts_aggregate_to_one_recipe_and_ignore_unlinked_posts(
    db_session, ranking_data,
):
    user, create = ranking_data
    recipe, first = create("Shared recipe")
    second = Post(author_id=user.id, recipe_id=recipe.id, caption="Again", image_url="/test.jpg")
    unlinked = Post(author_id=user.id, caption="No recipe", image_url="/test.jpg")
    db_session.add_all([second, unlinked])
    db_session.flush()
    for post in [first, second, unlinked]:
        db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.flush()
    items = rank(db_session)
    assert len(items) == 1 and items[0].recipe.id == recipe.id
    assert items[0].score == pytest.approx(6.0)
    assert items[0].likes_count == 2


def test_stable_pagination_and_no_activity_exclusion(db_session, ranking_data):
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


def test_custom_weights_can_disable_completion_signal(db_session, ranking_data):
    user, create = ranking_data
    recipe, _ = create("Cooked")
    db_session.add(CompletedRecipe(user_id=user.id, recipe_id=recipe.id, cooked_at=NOW))
    db_session.flush()
    assert rank(db_session, completion_weight=8.0)[0].score == pytest.approx(8.0)
    assert rank(db_session, completion_weight=0.0) == []


@pytest.mark.parametrize("overrides", [
    {"limit": 0}, {"limit": 101}, {"offset": -1}, {"window_days": 0},
    {"decay_hours": 0}, {"like_weight": -1}, {"comment_weight": float("nan")},
    {"completion_weight": float("inf")}, {"now": NOW.replace(tzinfo=None)},
])
def test_invalid_policy_is_rejected(db_session, overrides):
    with pytest.raises(ValueError):
        # Override the clock separately because rank() normally fixes it for all cases.
        values = {"now": NOW, **POLICY, **overrides}
        rank_trending_recipes(db_session, **values)


def test_utc_offset_clock_represents_same_instant(db_session, ranking_data):
    user, create = ranking_data
    _, post = create("Same instant")
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    db_session.flush()
    local_clock = NOW.astimezone(timezone(timedelta(hours=-8)))
    items = rank_trending_recipes(db_session, now=local_clock, **POLICY)
    assert items[0].score == pytest.approx(rank(db_session)[0].score)


def test_ranking_executes_one_read_query_without_changing_data(db_session, ranking_data):
    from sqlalchemy import event

    user, create = ranking_data
    recipe, post = create("Read-only")
    db_session.add(PostLike(user_id=user.id, post_id=post.id, created_at=NOW))
    # Collection eager joins must not duplicate ranked recipes or their scores.
    recipe.tags = [Tag(name="quick"), Tag(name="dinner")]
    db_session.commit()
    statements = []
    engine = db_session.get_bind()

    def record_query(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record_query)
    try:
        assert rank(db_session)[0].recipe.id == recipe.id
    finally:
        event.remove(engine, "before_cursor_execute", record_query)
    assert len(statements) == 1
    assert statements[0].lstrip().upper().startswith("SELECT")
    assert not db_session.new and not db_session.dirty and not db_session.deleted
