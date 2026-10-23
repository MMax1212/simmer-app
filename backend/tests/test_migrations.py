from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[1]


def test_account_database_migrates_and_preserves_accounts(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'accounts.db'}")
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    assert set(inspect(engine).get_table_names()) == {"users", "admin_audit", "alembic_version"}
    assert {c["name"] for c in inspect(engine).get_columns("users")} == {
        "id", "email", "username", "hashed_password", "role", "is_active", "created_at"}
    with engine.begin() as connection:
        connection.execute(text("""INSERT INTO users
            (id,email,username,hashed_password,role,is_active,created_at)
            VALUES (1,'ana@example.com','ana','hash','user',1,'2026-10-12')"""))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        assert connection.scalar(text("SELECT username FROM users WHERE id=1")) == "ana"
    engine.dispose()
