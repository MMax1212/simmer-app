"""Tests for US3.1.1: Community Dish Posts Relational Model & Schema.

Each test is mapped directly to an acceptance criterion in docs/tasks/sprint-3/US3.1.1.md.
"""
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.models import Post, Recipe, User


def test_US3_1_1_criterion_1_posts_table_schema_and_columns(db_session):
    """US3.1.1 Criterion 1: Table schema creates with required columns, types, and indexes."""
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()
    assert "posts" in tables

    columns = {col["name"]: col for col in inspector.get_columns("posts")}
    assert "id" in columns
    assert "author_id" in columns
    assert "caption" in columns
    assert "image_url" in columns
    assert "media_type" in columns
    assert "recipe_id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

    # Verify non-null constraints
    assert columns["image_url"]["nullable"] is False
    assert columns["caption"]["nullable"] is False
    assert columns["recipe_id"]["nullable"] is True

    # Verify indexes
    indexes = [idx["name"] for idx in inspector.get_indexes("posts")]
    assert any("author_id" in idx for idx in indexes)
    assert any("created_at" in idx for idx in indexes)


def test_US3_1_1_criterion_2_create_post_with_photo_and_video(db_session):
    """US3.1.1 Criterion 2: Persist posts with author, caption, media URL, media_type, and recipe."""
    author = User(email="chef@example.com", username="chef", hashed_password="pw")
    db_session.add(author)
    db_session.commit()

    recipe = Recipe(title="Homemade Ramen", description="Broth & noodles", author_id=author.id)
    db_session.add(recipe)
    db_session.commit()

    # Image post
    image_post = Post(
        author_id=author.id,
        caption="Delicious bowl of shoyu ramen!",
        image_url="https://images.unsplash.com/photo-ramen.jpg",
        media_type="image",
        recipe_id=recipe.id,
    )
    db_session.add(image_post)
    db_session.commit()
    db_session.refresh(image_post)

    assert image_post.id is not None
    assert image_post.author.username == "chef"
    assert image_post.recipe.title == "Homemade Ramen"
    assert image_post.media_type == "image"

    # Video review / mukbang post
    video_post = Post(
        author_id=author.id,
        caption="Ramen tasting & mukbang review!",
        image_url="https://cdn.simmer.app/videos/ramen_review.mp4",
        media_type="video",
    )
    db_session.add(video_post)
    db_session.commit()
    db_session.refresh(video_post)

    assert video_post.id is not None
    assert video_post.media_type == "video"
    assert video_post.recipe_id is None
    assert len(author.posts) == 2


def test_US3_1_1_criterion_3_post_without_media_rejected(db_session):
    """US3.1.1 Criterion 3: Persisting a post with image_url=None violates non-null constraint."""
    author = User(email="author_nomedia@example.com", username="author_nomedia", hashed_password="pw")
    db_session.add(author)
    db_session.commit()

    # Attempt to persist without image_url
    invalid_post = Post(author_id=author.id, caption="Post with no media", image_url=None)
    db_session.add(invalid_post)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_US3_1_1_criterion_4_delete_author_cascades_posts(db_session):
    """US3.1.1 Criterion 4: Deleting a user cascades and deletes all their posts."""
    author = User(email="deleted_author@example.com", username="deleted_author", hashed_password="pw")
    db_session.add(author)
    db_session.commit()

    p1 = Post(author_id=author.id, caption="First post", image_url="https://img.com/1.jpg")
    p2 = Post(author_id=author.id, caption="Second post", image_url="https://img.com/2.jpg")
    db_session.add_all([p1, p2])
    db_session.commit()

    p1_id, p2_id = p1.id, p2.id

    # Delete the user
    db_session.delete(author)
    db_session.commit()

    # Posts authored by this user must no longer exist
    assert db_session.get(Post, p1_id) is None
    assert db_session.get(Post, p2_id) is None


def test_US3_1_1_criterion_5_delete_recipe_sets_null_on_post(db_session):
    """US3.1.1 Criterion 5: Deleting a linked recipe preserves the post and sets recipe_id to None."""
    author = User(email="baker@example.com", username="baker", hashed_password="pw")
    db_session.add(author)
    db_session.commit()

    recipe = Recipe(title="Sourdough Loaf", description="Crusty bread", author_id=author.id)
    db_session.add(recipe)
    db_session.commit()

    post = Post(
        author_id=author.id,
        caption="Fresh sourdough loaf out of the Dutch oven!",
        image_url="https://img.com/bread.jpg",
        recipe_id=recipe.id,
    )
    db_session.add(post)
    db_session.commit()
    post_id = post.id

    # Delete the recipe
    db_session.delete(recipe)
    db_session.commit()

    # The post must still exist in the database, with recipe_id set to None
    persisted_post = db_session.get(Post, post_id)
    assert persisted_post is not None
    assert persisted_post.recipe_id is None
    assert persisted_post.caption == "Fresh sourdough loaf out of the Dutch oven!"
