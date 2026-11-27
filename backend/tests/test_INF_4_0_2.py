"""
backend/tests/test_INF_4_0_2.py — Automated Verification for Task INF-4.0.2
========================================================================================
Task ID: INF-4.0.2
Story:   INF-4.0 (Production Staging Deployment)
Author:  John Weaver

This test suite validates staging cloud database connectivity, configuration parsing,
transport layer encryption (SSL), object connection pooling, secret invariants,
and the /api/health/db diagnostic endpoint:
  1. Cloud database URL normalization (postgres:// -> postgresql://)
  2. Cloud PostgreSQL SSL query parameter injection (sslmode=require)
  3. Secret key validation invariants for staging and production environments
  4. Connection pooling configuration and database diagnostic check utility
  5. GET /api/health/db endpoint success response (HTTP 200, latency, dialect)
  6. GET /api/health/db endpoint failure response (HTTP 503 on database drop)
========================================================================================
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.database import check_database_connection
from app.main import app


def test_INF_4_0_2_criterion_1_url_normalization_postgres_prefix():
    """
    Acceptance Criterion 1:
    Cloud providers (AWS RDS, Neon, Supabase, Render) often emit legacy
    'postgres://' URIs. Settings.normalized_database_url must convert
    'postgres://' to SQLAlchemy 2.0-compatible 'postgresql://'.
    """
    cloud_url = "postgres://staging_user:secure_pwd@ep-simmer-staging.aws.neon.tech/simmer_db"
    s = Settings(database_url=cloud_url)

    assert s.normalized_database_url.startswith("postgresql://"), (
        "normalized_database_url must convert 'postgres://' to 'postgresql://'"
    )
    assert "staging_user:secure_pwd" in s.normalized_database_url
    assert "ep-simmer-staging.aws.neon.tech/simmer_db" in s.normalized_database_url


def test_INF_4_0_2_criterion_2_ssl_mode_injection():
    """
    Acceptance Criterion 2:
    When db_ssl_mode is set (e.g., 'require'), PostgreSQL connections must
    have 'sslmode=require' injected into the connection query string to enforce
    TLS/SSL encrypted transport across public cloud networks.
    SQLite connections must never have SSL flags injected.
    """
    # Test 1: PostgreSQL URL without query params receives sslmode
    pg_url = "postgresql://simmer_user:pwd@db.staging.render.com/simmer"
    s_pg = Settings(database_url=pg_url, db_ssl_mode="require")
    assert "sslmode=require" in s_pg.normalized_database_url, (
        "PostgreSQL connection must include sslmode=require"
    )

    # Test 2: PostgreSQL URL with existing parameters preserves them and appends sslmode
    pg_with_params = "postgresql://simmer_user:pwd@db.staging.render.com/simmer?connect_timeout=10"
    s_pg_params = Settings(database_url=pg_with_params, db_ssl_mode="require")
    assert "sslmode=require" in s_pg_params.normalized_database_url
    assert "connect_timeout=10" in s_pg_params.normalized_database_url

    # Test 3: Existing sslmode is not duplicated
    pg_already_ssl = "postgresql://simmer_user:pwd@db.staging.render.com/simmer?sslmode=verify-full"
    s_already_ssl = Settings(database_url=pg_already_ssl, db_ssl_mode="require")
    assert s_already_ssl.normalized_database_url.count("sslmode") == 1
    assert "sslmode=verify-full" in s_already_ssl.normalized_database_url

    # Test 4: Local SQLite URLs remain untouched
    sqlite_url = "sqlite:///./test.db"
    s_sqlite = Settings(database_url=sqlite_url, db_ssl_mode="require")
    assert s_sqlite.normalized_database_url == "sqlite:///./test.db"
    assert "sslmode" not in s_sqlite.normalized_database_url


def test_INF_4_0_2_criterion_3_staging_production_secret_key_invariants():
    """
    Acceptance Criterion 3:
    In 'staging' or 'production' mode, the application MUST reject default development
    keys or keys with insufficient entropy (<32 characters) to guard against security breaches.
    In 'development' mode, the default key is accepted for developer convenience.
    """
    default_insecure_key = "dev-only-insecure-secret-change-me"
    secure_staging_key = "a_very_secure_production_key_with_at_least_32_characters!"

    # Case A: Development mode allows default key
    dev_settings = Settings(environment="development", secret_key=default_insecure_key)
    assert dev_settings.secret_key == default_insecure_key

    # Case B: Staging mode REJECTS default key
    with pytest.raises(ValueError, match="CRITICAL SECURITY INVARIANT VIOLATION"):
        Settings(environment="staging", secret_key=default_insecure_key)

    # Case C: Production mode REJECTS default key
    with pytest.raises(ValueError, match="CRITICAL SECURITY INVARIANT VIOLATION"):
        Settings(environment="production", secret_key=default_insecure_key)

    # Case D: Staging mode REJECTS short keys (< 32 characters)
    with pytest.raises(ValueError, match="CRITICAL SECURITY INVARIANT VIOLATION"):
        Settings(environment="staging", secret_key="short_16_char_key!")

    # Case E: Staging mode ACCEPTS strong key
    staging_settings = Settings(environment="staging", secret_key=secure_staging_key)
    assert staging_settings.secret_key == secure_staging_key


def test_INF_4_0_2_criterion_4_connection_pooling_and_check_diagnostic(db_session):
    """
    Acceptance Criterion 4:
    Settings exposes pooling configuration (db_pool_size, db_max_overflow,
    db_pool_timeout, db_pool_pre_ping) and check_database_connection correctly
    probes liveness and reports latency.
    """
    s = Settings()
    assert s.db_pool_size >= 1
    assert s.db_max_overflow >= 0
    assert s.db_pool_timeout > 0
    assert s.db_pool_pre_ping is True

    # Test the diagnostic probe utility with an active database session
    diag = check_database_connection(db_session)
    assert diag["status"] == "ok"
    assert diag["database"] == "connected"
    assert "dialect" in diag
    assert isinstance(diag["latency_ms"], float)
    assert diag["latency_ms"] >= 0.0


def test_INF_4_0_2_criterion_5_health_db_endpoint_success(client: TestClient):
    """
    Acceptance Criterion 5:
    GET /api/health/db queries the active database connection pool, confirms
    liveness via 'SELECT 1', and returns HTTP 200 with connection metadata.
    """
    response = client.get("/api/health/db")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "dialect" in data
    assert "latency_ms" in data
    assert isinstance(data["latency_ms"], (int, float))


def test_INF_4_0_2_criterion_6_health_db_endpoint_failure(client: TestClient):
    """
    Acceptance Criterion 6:
    When the database is unreachable or connection fails, GET /api/health/db
    must return HTTP 503 Service Unavailable with diagnostic error information.
    """
    with patch("app.main.check_database_connection", side_effect=Exception("Database socket connection timed out")):
        response = client.get("/api/health/db")
        assert response.status_code == 503

        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
        assert "Database socket connection timed out" in data["error"]
