"""Tests for US4.4.1: Curated Dietary and Occasion Tag Seeds and Schema.

Mapped directly to acceptance criteria in docs/tasks/sprint-4/US4.4.1.md.
"""
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.models import Recipe, Tag, User

ROOT = Path(__file__).resolve().parents[1]

CURATED_DIETARY_TAGS = [
    "#vegan",
    "#vegetarian",
    "#gluten-free",
    "#keto",
    "#low-carb",
    "#dairy-free",
    "#nut-free",
]

CURATED_OCCASION_TAGS = [
    "#quick-dinner",
    "#under-30-mins",
    "#date-night",
    "#meal-prep",
    "#comfort-food",
    "#kid-friendly",
]

ALL_CURATED_TAGS = CURATED_DIETARY_TAGS + CURATED_OCCASION_TAGS


def _run_migrations(engine, revision="head"):
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def test_US4_4_1_criterion_1_dietary_tags_seeded(tmp_path):
    """US4.4.1 Criterion 1: The tags table contains all 7 curated dietary tags."""
    db_path = tmp_path / "test_dietary.db"
    engine = create_engine(f"sqlite:///{db_path}")
    _run_migrations(engine)

    with Session(engine) as session:
        stored_tags = {tag.name for tag in session.scalars(select(Tag)).all()}
        for dietary_tag in CURATED_DIETARY_TAGS:
            assert dietary_tag in stored_tags, f"Expected dietary tag {dietary_tag} in tags table"
    engine.dispose()


def test_US4_4_1_criterion_2_occasion_tags_seeded(tmp_path):
    """US4.4.1 Criterion 2: The tags table contains all 6 curated occasion tags."""
    db_path = tmp_path / "test_occasion.db"
    engine = create_engine(f"sqlite:///{db_path}")
    _run_migrations(engine)

    with Session(engine) as session:
        stored_tags = {tag.name for tag in session.scalars(select(Tag)).all()}
        for occasion_tag in CURATED_OCCASION_TAGS:
            assert occasion_tag in stored_tags, f"Expected occasion tag {occasion_tag} in tags table"
    engine.dispose()


def test_US4_4_1_criterion_3_lowercase_and_hash_prefixed(tmp_path):
    """US4.4.1 Criterion 3: All seeded tag names are stored in lowercase format with a leading '#' prefix."""
    db_path = tmp_path / "test_format.db"
    engine = create_engine(f"sqlite:///{db_path}")
    _run_migrations(engine)

    with Session(engine) as session:
        tags = session.scalars(select(Tag).where(Tag.name.in_(ALL_CURATED_TAGS))).all()
        assert len(tags) == len(ALL_CURATED_TAGS)
        for tag in tags:
            assert tag.name.startswith("#"), f"Tag {tag.name} must start with '#'"
            assert tag.name == tag.name.lower(), f"Tag {tag.name} must be lowercase"
    engine.dispose()


def test_US4_4_1_criterion_4_idempotent_migration(tmp_path):
    """US4.4.1 Criterion 4: Running migration repeatedly or on existing tags does not produce duplicates or errors."""
    db_path = tmp_path / "test_idempotency.db"
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Pre-populate one of the tags before migration
    _run_migrations(engine, "0009_user_follows")
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO tags (name) VALUES ('#vegan')"))
    
    # Run migration 0010 (head)
    _run_migrations(engine, "head")
    
    # Re-run migration to assert idempotency
    _run_migrations(engine, "head")

    with Session(engine) as session:
        vegan_tags = session.scalars(select(Tag).where(Tag.name == "#vegan")).all()
        assert len(vegan_tags) == 1, "Expected exactly 1 '#vegan' tag without duplicates"
        
        all_tags = session.scalars(select(Tag).where(Tag.name.in_(ALL_CURATED_TAGS))).all()
        assert len(all_tags) == len(ALL_CURATED_TAGS)
    engine.dispose()


def test_US4_4_1_criterion_5_recipe_association(tmp_path):
    """US4.4.1 Criterion 5: A recipe can be associated with multiple curated dietary and occasion tags."""
    db_path = tmp_path / "test_recipe_assoc.db"
    engine = create_engine(f"sqlite:///{db_path}")
    _run_migrations(engine)

    with Session(engine) as session:
        user = User(email="chef@example.com", username="chef", hashed_password="pw")
        session.add(user)
        session.commit()

        recipe = Recipe(
            author_id=user.id,
            title="Zucchini Noodles",
            description="Low carb vegan noodles",
            cook_time_mins=15,
            prep_time_mins=10,
        )
        session.add(recipe)
        session.commit()

        # Associate multiple curated tags
        vegan_tag = session.scalar(select(Tag).where(Tag.name == "#vegan"))
        quick_tag = session.scalar(select(Tag).where(Tag.name == "#under-30-mins"))
        gluten_free_tag = session.scalar(select(Tag).where(Tag.name == "#gluten-free"))

        assert vegan_tag is not None
        assert quick_tag is not None
        assert gluten_free_tag is not None

        recipe.tags.extend([vegan_tag, quick_tag, gluten_free_tag])
        session.commit()

        # Query back and verify association
        saved_recipe = session.scalar(select(Recipe).where(Recipe.id == recipe.id))
        tag_names = {t.name for t in saved_recipe.tags}
        assert {"#vegan", "#under-30-mins", "#gluten-free"}.issubset(tag_names)
    engine.dispose()


def test_US4_4_1_criterion_6_migration_upgrade_and_downgrade(tmp_path):
    """US4.4.1 Criterion 6: Migration 0010 upgrades and downgrades cleanly."""
    db_path = tmp_path / "test_migration_cycle.db"
    engine = create_engine(f"sqlite:///{db_path}")
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))

    # Upgrade to head
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")

    with Session(engine) as session:
        # Verify tags are present after upgrade
        tag_count = len(session.scalars(select(Tag).where(Tag.name.in_(ALL_CURATED_TAGS))).all())
        assert tag_count == len(ALL_CURATED_TAGS)

    # Downgrade back to 0009_user_follows
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "0009_user_follows")

    with Session(engine) as session:
        # Verify curated tags removed
        curated_tags_remaining = session.scalars(select(Tag).where(Tag.name.in_(ALL_CURATED_TAGS))).all()
        assert len(curated_tags_remaining) == 0

    engine.dispose()
