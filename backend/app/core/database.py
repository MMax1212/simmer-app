"""
backend/app/core/database.py — Database Engine, Connection Pooling & Health Monitoring
======================================================================================
Architectural Overview (INF-4.0.2):
This module manages the database lifecycle using SQLAlchemy 2.0:
  1. Connection Pooling (C++ Object Pool): Reuses persistent TCP connections for cloud DBs
  2. Pre-Ping Liveness: Discards stale/closed cloud sockets before executing queries
  3. Dialect Adaptability: Seamlessly supports SQLite (local) and PostgreSQL (cloud staging)
  4. Health Diagnostic: Provides connection latency and liveness probing (SELECT 1)
======================================================================================
"""

import time
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# ------------------------------------------------------------------------------
# Engine & Connection Pool Initialization
# ------------------------------------------------------------------------------
# In C++, creating a new socket, performing TLS handshakes, and authenticating on
# every query is very expensive. SQLAlchemy's engine maintains a pool of persistent
# open connection sockets that worker threads borrow and return.

is_sqlite = settings.normalized_database_url.startswith("sqlite")

# SQLite requires check_same_thread=False because FastAPI handles requests on
# a threadpool, while PostgreSQL handles multi-threaded pooling natively.
connect_args: dict[str, Any] = {"check_same_thread": False} if is_sqlite else {}

# Connection pooling keyword arguments
engine_kwargs: dict[str, Any] = {
    "connect_args": connect_args,
    # pool_pre_ping: Sends a lightweight ping query ("SELECT 1") before handing
    # a socket connection to a query. If the cloud database dropped an idle TCP
    # connection, SQLAlchemy automatically reconnects instead of raising an error.
    "pool_pre_ping": settings.db_pool_pre_ping,
}

# Non-SQLite databases (PostgreSQL in cloud staging) support custom pool sizing
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
    })

engine = create_engine(settings.normalized_database_url, **engine_kwargs)

# For SQLite, enforce relational foreign key cascade constraints
if is_sqlite:
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute(text("PRAGMA foreign_keys=ON"))

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: Borrows one database session/connection from the pool
    per incoming HTTP request, ensuring it is always returned/closed afterwards (RAII pattern).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection(db_or_engine: Session | Any = None) -> dict[str, Any]:
    """
    Performs a liveness diagnostic probe against the active database:
    1. Executes a minimal 'SELECT 1' query.
    2. Measures query round-trip latency in milliseconds.
    3. Identifies the active database dialect (sqlite, postgresql).
    Returns a diagnostic status dict, or raises an exception if unreachable.
    """
    start_time = time.perf_counter()

    if isinstance(db_or_engine, Session):
        db_or_engine.execute(text("SELECT 1"))
        dialect = db_or_engine.bind.dialect.name if db_or_engine.bind else "unknown"
    else:
        target_engine = db_or_engine or engine
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        dialect = target_engine.dialect.name

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "status": "ok",
        "database": "connected",
        "dialect": dialect,
        "latency_ms": latency_ms,
    }
