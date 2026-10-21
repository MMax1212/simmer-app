from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app

ROOT = Path(__file__).resolve().parents[1]


def migrate(engine, revision="head"):
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def test_fresh_database_upgrades_and_can_store_complete_recipe(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    migrate(engine)
    migrate(engine)  # Re-running the upgrade must be safe.
    assert {"users", "recipes", "recipe_ingredients", "recipe_steps", "admin_audit"}.issubset(inspect(engine).get_table_names())
    with Session(engine) as session:
        app.dependency_overrides[get_db] = lambda: session
        try:
            with TestClient(app) as client:
                assert client.post("/api/v1/auth/register", json={
                    "email": "fresh@example.com", "username": "fresh", "password": "password123"}).status_code == 201
                login = client.post("/api/v1/auth/login", json={"username_or_email": "fresh", "password": "password123"})
                h = {"Authorization": "Bearer " + login.json()["access_token"]}
                from tests.test_recipes import PASTA
                assert client.post("/api/v1/recipes", headers=h, json=PASTA).status_code == 201
        finally:
            app.dependency_overrides.clear()
    engine.dispose()


def test_existing_unversioned_database_preserves_accounts_recipes_and_unknown_measurements(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    migrate(engine, "0001")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE alembic_version"))  # Simulate John's unversioned create_all database.
        conn.execute(text("""INSERT INTO users
            (id,email,username,hashed_password,role,is_active,created_at,dietary_prefs,bio)
            VALUES (7,'legacy@example.com','legacy',:password,'user',1,'2026-10-12','null','Existing bio')"""),
            {"password": hash_password("password123")})
        conn.execute(text("""INSERT INTO recipes
            (id,owner_id,title,instructions,created_at,updated_at)
            VALUES (9,7,'Legacy pasta',:instructions,'2026-10-12','2026-10-12')"""),
            {"instructions": "1. Boil pasta.\n2. Add sauce."})
        conn.execute(text("""INSERT INTO ingredients (id,recipe_id,position,name,quantity,unit)
            VALUES (10,9,0,'Pasta',400,'g'),(11,9,1,'Salt',NULL,NULL)"""))
    migrate(engine)
    with Session(engine) as session:
        app.dependency_overrides[get_db] = lambda: session
        try:
            with TestClient(app) as client:
                login = client.post("/api/v1/auth/login", json={
                    "username_or_email": "legacy", "password": "password123"})
                assert login.status_code == 200
                assert login.json()["user"]["bio"] == "Existing bio"
                assert login.json()["user"]["culinary_preferences"] == []
                recipe = client.get("/api/v1/recipes/9").json()
                assert recipe["author_id"] == 7
                assert recipe["ingredients"][0]["id"] == 10
                assert recipe["ingredients"][0]["amount"] == 400
                assert recipe["ingredients"][1]["amount"] is None
                assert [s["instruction"] for s in recipe["steps"]] == ["1. Boil pasta.", "2. Add sauce."]
                assert recipe["prep_time_mins"] == 0 and recipe["servings"] == 1
        finally:
            app.dependency_overrides.clear()
    engine.dispose()
