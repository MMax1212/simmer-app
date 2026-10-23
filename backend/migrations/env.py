from alembic import context
from sqlalchemy import create_engine, pool

from app import models
from app.core.config import settings
from app.core.database import Base

config = context.config
target_metadata = Base.metadata


def run_migrations(connection):


    if connection.dialect.name == "sqlite" and not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True,
                      transactional_ddl=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Use online migrations so legacy data can be preserved.")
elif config.attributes.get("connection") is not None:
    run_migrations(config.attributes["connection"])
else:

    url = config.attributes.get("database_url", settings.database_url)
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.begin() as connection:
        run_migrations(connection)
    engine.dispose()
