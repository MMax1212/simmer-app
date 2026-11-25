"""Tests for US4.2.2: Design and create grocery_lists and grocery_items database tables.

Mapped directly to acceptance criteria in docs/tasks/sprint-4/US4.2.2.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import GroceryItem, GroceryList, Recipe, User

ROOT = Path(__file__).resolve().parents[1]


def _run_migrations(engine, revision="head"):
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def test_US4_2_2_criterion_1_grocery_lists_schema(db_session):
    """Criterion 1: grocery_lists schema creates with required columns and persists with FK."""
    inspector = inspect(db_session.bind)
    assert "grocery_lists" in inspector.get_table_names()

    columns = {col["name"]: col for col in inspector.get_columns("grocery_lists")}
    assert "id" in columns
    assert "user_id" in columns
    assert "title" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

    user = User(email="chef_gl@test.com", username="chef_gl", hashed_password="pw")
    db_session.add(user)
    db_session.commit()

    glist = GroceryList(user_id=user.id, title="Weekly Shop")
    db_session.add(glist)
    db_session.commit()

    saved = db_session.scalar(select(GroceryList).where(GroceryList.id == glist.id))
    assert saved is not None
    assert saved.title == "Weekly Shop"
    assert saved.user_id == user.id
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_US4_2_2_criterion_2_grocery_items_schema(db_session):
    """Criterion 2: grocery_items persists with foreign keys to list and nullable recipe."""
    inspector = inspect(db_session.bind)
    assert "grocery_items" in inspector.get_table_names()

    columns = {col["name"]: col for col in inspector.get_columns("grocery_items")}
    assert "id" in columns
    assert "grocery_list_id" in columns
    assert "name" in columns
    assert "amount" in columns
    assert "unit" in columns
    assert "department" in columns
    assert "is_checked" in columns
    assert "source_recipe_id" in columns
    assert "created_at" in columns

    user = User(email="chef_gi@test.com", username="chef_gi", hashed_password="pw")
    db_session.add(user)
    db_session.commit()

    recipe = Recipe(title="Pasta Carbonara", author_id=user.id)
    db_session.add(recipe)
    db_session.commit()

    glist = GroceryList(user_id=user.id, title="Carbonara List")
    db_session.add(glist)
    db_session.commit()

    item = GroceryItem(
        grocery_list_id=glist.id,
        name="parmesan cheese",
        amount=1.5,
        unit="cup",
        department="Dairy & Refrigerated",
        source_recipe_id=recipe.id,
    )
    db_session.add(item)
    db_session.commit()

    saved = db_session.scalar(select(GroceryItem).where(GroceryItem.id == item.id))
    assert saved is not None
    assert saved.name == "parmesan cheese"
    assert saved.amount == 1.5
    assert saved.unit == "cup"
    assert saved.department == "Dairy & Refrigerated"
    assert saved.is_checked is False
    assert saved.source_recipe_id == recipe.id


def test_US4_2_2_criterion_3_amount_positive_check_constraint(tmp_path):
    """Criterion 3: Check constraint amount > 0 rejects zero or negative amounts."""
    db_path = tmp_path / "test_constraint.db"
    engine = create_engine(f"sqlite:///{db_path}")
    _run_migrations(engine)

    with Session(engine) as session:
        user = User(email="chef_check@test.com", username="chef_check", hashed_password="pw")
        session.add(user)
        session.commit()

        glist = GroceryList(user_id=user.id, title="Constraint List")
        session.add(glist)
        session.commit()

        # Zero amount must fail
        zero_item = GroceryItem(
            grocery_list_id=glist.id,
            name="salt",
            amount=0.0,
            unit="tsp",
            department="Pantry & Baking",
        )
        session.add(zero_item)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        # Negative amount must fail
        neg_item = GroceryItem(
            grocery_list_id=glist.id,
            name="sugar",
            amount=-2.0,
            unit="cup",
            department="Pantry & Baking",
        )
        session.add(neg_item)
        with pytest.raises(IntegrityError):
            session.commit()


def test_US4_2_2_criterion_4_user_cascade_deletion(db_session):
    """Criterion 4: Deleting a user cascades and deletes all associated grocery lists and items."""
    user = User(email="chef_del@test.com", username="chef_del", hashed_password="pw")
    db_session.add(user)
    db_session.commit()

    glist = GroceryList(user_id=user.id, title="To Delete")
    db_session.add(glist)
    db_session.commit()

    item = GroceryItem(
        grocery_list_id=glist.id,
        name="butter",
        amount=1.0,
        unit="cup",
        department="Dairy & Refrigerated",
    )
    db_session.add(item)
    db_session.commit()
    list_id, item_id = glist.id, item.id

    db_session.delete(user)
    db_session.commit()

    assert db_session.scalar(select(GroceryList).where(GroceryList.id == list_id)) is None
    assert db_session.scalar(select(GroceryItem).where(GroceryItem.id == item_id)) is None


def test_US4_2_2_criterion_5_recipe_set_null_deletion(db_session):
    """Criterion 5: Deleting a recipe sets source_recipe_id=NULL without deleting the item."""
    user = User(email="chef_recipe_del@test.com", username="chef_rd", hashed_password="pw")
    db_session.add(user)
    db_session.commit()

    recipe = Recipe(title="Garden Salad", author_id=user.id)
    db_session.add(recipe)
    db_session.commit()

    glist = GroceryList(user_id=user.id, title="Salad List")
    db_session.add(glist)
    db_session.commit()

    item = GroceryItem(
        grocery_list_id=glist.id,
        name="romaine lettuce",
        amount=2.0,
        unit="head",
        department="Produce",
        source_recipe_id=recipe.id,
    )
    db_session.add(item)
    db_session.commit()
    item_id = item.id

    db_session.delete(recipe)
    db_session.commit()

    saved_item = db_session.scalar(select(GroceryItem).where(GroceryItem.id == item_id))
    assert saved_item is not None
    assert saved_item.name == "romaine lettuce"
    assert saved_item.source_recipe_id is None


def test_US4_2_2_criterion_6_migration_upgrade_and_downgrade(tmp_path):
    """Criterion 6: Migration executes clean upgrade and downgrade."""
    db_path = tmp_path / "test_migration.db"
    engine = create_engine(f"sqlite:///{db_path}")
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        # Upgrade to head (includes 0011)
        command.upgrade(config, "0011_grocery_lists_and_items")

        # Verify tables created
        inspector = inspect(connection)
        assert "grocery_lists" in inspector.get_table_names()
        assert "grocery_items" in inspector.get_table_names()

        # Downgrade back to 0010
        command.downgrade(config, "0010_dietary_and_occasion_tag_seeds")
        inspector = inspect(connection)
        assert "grocery_lists" not in inspector.get_table_names()
        assert "grocery_items" not in inspector.get_table_names()

        # Re-upgrade cleanly
        command.upgrade(config, "0011_grocery_lists_and_items")
        inspector = inspect(connection)
        assert "grocery_lists" in inspector.get_table_names()
        assert "grocery_items" in inspector.get_table_names()
