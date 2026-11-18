"""Tests for US3.3.1: Post Likes & Comments Relational Schema and Models.

Mapped directly to acceptance criteria in docs/tasks/sprint-3/US3.3.1.md.
"""
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError

from app.models import Post, PostComment, PostLike, Recipe, User

ROOT = Path(__file__).resolve().parents[1]


def test_US3_3_1_criterion_1_post_likes_schema(db_session):
    """US3.3.1 Criterion 1: post_likes table creates with required columns, constraints, and indexes."""
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()
    assert "post_likes" in tables

    columns = {col["name"]: col for col in inspector.get_columns("post_likes")}
    assert "id" in columns
    assert "user_id" in columns
    assert "post_id" in columns
    assert "created_at" in columns

    # Non-null constraints
    assert columns["user_id"]["nullable"] is False
    assert columns["post_id"]["nullable"] is False

    # Index on post_id
    indexes = [idx["name"] for idx in inspector.get_indexes("post_likes")]
    assert any("post_id" in idx for idx in indexes)

    # Unique constraint on (user_id, post_id)
    unique_constraints = inspector.get_unique_constraints("post_likes")
    unique_col_sets = [set(uc["column_names"]) for uc in unique_constraints]
    # Check either unique constraint or unique index covering (user_id, post_id)
    has_unique = {"user_id", "post_id"} in unique_col_sets or any(
        {"user_id", "post_id"} == set(idx.get("column_names", [])) and idx.get("unique")
        for idx in inspector.get_indexes("post_likes")
    )
    assert has_unique, "Unique constraint or index on (user_id, post_id) must exist"


def test_US3_3_1_criterion_2_post_comments_schema(db_session):
    """US3.3.1 Criterion 2: post_comments table creates with required columns and indexes."""
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()
    assert "post_comments" in tables

    columns = {col["name"]: col for col in inspector.get_columns("post_comments")}
    assert "id" in columns
    assert "user_id" in columns
    assert "post_id" in columns
    assert "content" in columns
    assert "created_at" in columns

    # Non-null constraints
    assert columns["user_id"]["nullable"] is False
    assert columns["post_id"]["nullable"] is False
    assert columns["content"]["nullable"] is False

    # Index on post_id and created_at
    indexes = [idx["name"] for idx in inspector.get_indexes("post_comments")]
    assert any("post_id" in idx for idx in indexes)


def test_US3_3_1_criterion_3_prevent_duplicate_likes(db_session):
    """US3.3.1 Criterion 3: A user can like a post, and duplicate likes raise IntegrityError."""
    author = User(email="author1@example.com", username="author1", hashed_password="pw")
    liker = User(email="liker1@example.com", username="liker1", hashed_password="pw")
    db_session.add_all([author, liker])
    db_session.commit()

    post = Post(author_id=author.id, caption="Delicious pizza", image_url="https://img.com/pizza.jpg")
    db_session.add(post)
    db_session.commit()

    # First like succeeds
    like1 = PostLike(user_id=liker.id, post_id=post.id)
    db_session.add(like1)
    db_session.commit()
    assert like1.id is not None

    # Duplicate like by the same user on the same post must fail
    like2 = PostLike(user_id=liker.id, post_id=post.id)
    db_session.add(like2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_US3_3_1_criterion_4_comment_requires_non_null_content(db_session):
    """US3.3.1 Criterion 4: Attempting to persist a comment with null content raises IntegrityError."""
    author = User(email="author2@example.com", username="author2", hashed_password="pw")
    commenter = User(email="commenter2@example.com", username="commenter2", hashed_password="pw")
    db_session.add_all([author, commenter])
    db_session.commit()

    post = Post(author_id=author.id, caption="Pasta night", image_url="https://img.com/pasta.jpg")
    db_session.add(post)
    db_session.commit()

    # Valid comment succeeds
    comment = PostComment(user_id=commenter.id, post_id=post.id, content="Great presentation!")
    db_session.add(comment)
    db_session.commit()
    assert comment.id is not None

    # Null content fails
    invalid_comment = PostComment(user_id=commenter.id, post_id=post.id, content=None)
    db_session.add(invalid_comment)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_US3_3_1_criterion_5_delete_post_cascades_likes_and_comments(db_session):
    """US3.3.1 Criterion 5: Deleting a post cascades and removes all associated likes and comments."""
    author = User(email="author3@example.com", username="author3", hashed_password="pw")
    user2 = User(email="fan3@example.com", username="fan3", hashed_password="pw")
    db_session.add_all([author, user2])
    db_session.commit()

    post = Post(author_id=author.id, caption="Sushi rolls", image_url="https://img.com/sushi.jpg")
    db_session.add(post)
    db_session.commit()

    like = PostLike(user_id=user2.id, post_id=post.id)
    comment = PostComment(user_id=user2.id, post_id=post.id, content="Looks fresh!")
    db_session.add_all([like, comment])
    db_session.commit()

    like_id, comment_id = like.id, comment.id

    # Delete the post
    db_session.delete(post)
    db_session.commit()

    # Likes and comments must be deleted via cascade
    assert db_session.get(PostLike, like_id) is None
    assert db_session.get(PostComment, comment_id) is None


def test_US3_3_1_criterion_6_delete_user_cascades_likes_and_comments(db_session):
    """US3.3.1 Criterion 6: Deleting a user cascades and removes all likes and comments authored by them."""
    author = User(email="author4@example.com", username="author4", hashed_password="pw")
    engager = User(email="engager4@example.com", username="engager4", hashed_password="pw")
    db_session.add_all([author, engager])
    db_session.commit()

    post = Post(author_id=author.id, caption="Tacos", image_url="https://img.com/tacos.jpg")
    db_session.add(post)
    db_session.commit()

    like = PostLike(user_id=engager.id, post_id=post.id)
    comment = PostComment(user_id=engager.id, post_id=post.id, content="Yum!")
    db_session.add_all([like, comment])
    db_session.commit()

    like_id, comment_id = like.id, comment.id

    # Delete the engager user
    db_session.delete(engager)
    db_session.commit()

    # Their like and comment must be gone
    assert db_session.get(PostLike, like_id) is None
    assert db_session.get(PostComment, comment_id) is None
    # Post itself remains
    assert db_session.get(Post, post.id) is not None


def test_US3_3_1_criterion_7_orm_relationship_navigation(db_session):
    """US3.3.1 Criterion 7: ORM navigation properties on Post and User load likes and comments."""
    author = User(email="chef5@example.com", username="chef5", hashed_password="pw")
    fan = User(email="fan5@example.com", username="fan5", hashed_password="pw")
    db_session.add_all([author, fan])
    db_session.commit()

    post = Post(author_id=author.id, caption="Burgers", image_url="https://img.com/burger.jpg")
    db_session.add(post)
    db_session.commit()

    like = PostLike(user_id=fan.id, post_id=post.id)
    comment = PostComment(user_id=fan.id, post_id=post.id, content="Best burger!")
    db_session.add_all([like, comment])
    db_session.commit()

    # Post navigation
    db_session.refresh(post)
    assert len(post.likes) == 1
    assert post.likes[0].user_id == fan.id
    assert len(post.comments) == 1
    assert post.comments[0].content == "Best burger!"

    # User navigation
    db_session.refresh(fan)
    assert len(fan.post_likes) == 1
    assert len(fan.post_comments) == 1


def test_US3_3_1_criterion_8_alembic_migration_upgrade_and_downgrade(tmp_path):
    """US3.3.1 Criterion 8: Alembic migration 0007 upgrades and downgrades cleanly."""
    engine = create_engine(f"sqlite:///{tmp_path / 'migration_test.db'}")
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        # Upgrade to head
        command.upgrade(config, "head")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "post_likes" in tables
    assert "post_comments" in tables

    # Downgrade back to 0006
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "0006_completed_recipes")

    inspector_after = inspect(engine)
    tables_after = inspector_after.get_table_names()
    assert "post_likes" not in tables_after
    assert "post_comments" not in tables_after

    engine.dispose()
