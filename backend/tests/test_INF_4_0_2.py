"""
backend/tests/test_INF_4_0_2.py — Automated Verification for Task INF-4.0.2
========================================================================================
Task ID: INF-4.0.2
Story:   INF-4.0 (Production Staging Deployment)
Author:  John Weaver

Systems Programming & Cloud Networking Concepts Covered:
  1. URI Normalization (Handling vendor protocol string differences like postgres vs postgresql)
  2. Transport Layer Security / SSL (Ensuring encrypted TLS handshakes over public cloud TCP sockets)
  3. Security Invariants (Asserting minimum 256-bit cryptographic entropy in staging/production)
  4. Connection Pooling (The C++ Object Pool design pattern: reusing persistent TCP sockets)
  5. Socket Liveness Probing & Latency Benchmarking (SELECT 1 query benchmark in milliseconds)
  6. Fault-Tolerance Simulation (Mocking severed database sockets to verify HTTP 503 error handling)
========================================================================================
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.database import check_database_connection
from app.main import app


def test_INF_4_0_2_criterion_1_url_normalization_postgres_prefix():
    """
    Acceptance Criterion 1: Cloud Provider URL Compatibility.

    Problem in C++ / Systems terms:
    Different cloud providers (AWS RDS, Neon, Supabase, Render) output connection
    strings formatted as 'postgres://...'. However, SQLAlchemy 2.0 expects the standard
    dialect driver identifier 'postgresql://'. Passing 'postgres://' directly causes
    the driver to fail with an unknown protocol exception.

    Solution:
    Settings.normalized_database_url inspects the protocol prefix and automatically
    replaces 'postgres://' with 'postgresql://' while preserving all credentials and hosts.
    """
    cloud_url = "postgres://staging_user:secure_pwd@ep-simmer-staging.aws.neon.tech/simmer_db"
    s = Settings(database_url=cloud_url)

    # Verify protocol scheme was safely transformed to postgresql://
    assert s.normalized_database_url.startswith("postgresql://"), (
        "normalized_database_url must convert 'postgres://' to 'postgresql://'"
    )
    # Verify username, password, and hostname were not corrupted during string parsing
    assert "staging_user:secure_pwd" in s.normalized_database_url
    assert "ep-simmer-staging.aws.neon.tech/simmer_db" in s.normalized_database_url


def test_INF_4_0_2_criterion_2_ssl_mode_injection():
    """
    Acceptance Criterion 2: TLS/SSL Encrypted Transport.

    Problem in C++ / Systems terms:
    Connecting across the open internet to a remote cloud database sends packets over
    public routers. If unencrypted, passwords and SQL queries travel in plaintext.

    Solution:
    When db_ssl_mode='require', we inject 'sslmode=require' into the PostgreSQL query
    parameters. This forces the TCP socket client to perform a TLS cryptographic handshake
    before any application data is transmitted.
    Local SQLite files do NOT use network sockets, so SQLite URLs must remain untouched.
    """
    # Case 1: Plain PostgreSQL URL without query params receives ?sslmode=require
    pg_url = "postgresql://simmer_user:pwd@db.staging.render.com/simmer"
    s_pg = Settings(database_url=pg_url, db_ssl_mode="require")
    assert "sslmode=require" in s_pg.normalized_database_url, (
        "PostgreSQL connection must include sslmode=require"
    )

    # Case 2: PostgreSQL URL that already has existing query parameters preserves them
    pg_with_params = "postgresql://simmer_user:pwd@db.staging.render.com/simmer?connect_timeout=10"
    s_pg_params = Settings(database_url=pg_with_params, db_ssl_mode="require")
    assert "sslmode=require" in s_pg_params.normalized_database_url
    assert "connect_timeout=10" in s_pg_params.normalized_database_url

    # Case 3: If sslmode is already specified, do not append a duplicate parameter
    pg_already_ssl = "postgresql://simmer_user:pwd@db.staging.render.com/simmer?sslmode=verify-full"
    s_already_ssl = Settings(database_url=pg_already_ssl, db_ssl_mode="require")
    assert s_already_ssl.normalized_database_url.count("sslmode") == 1
    assert "sslmode=verify-full" in s_already_ssl.normalized_database_url

    # Case 4: Local SQLite file URLs are file descriptors on disk, so SSL is skipped
    sqlite_url = "sqlite:///./test.db"
    s_sqlite = Settings(database_url=sqlite_url, db_ssl_mode="require")
    assert s_sqlite.normalized_database_url == "sqlite:///./test.db"
    assert "sslmode" not in s_sqlite.normalized_database_url


def test_INF_4_0_2_criterion_3_staging_production_secret_key_invariants():
    """
    Acceptance Criterion 3: Environment-Gated Security Assertions.

    Problem in C++ / Systems terms:
    Similar to compile-time '#ifndef NDEBUG' assertion guards, we must prevent the
    application from booting in staging or production if someone accidentally forgot
    to configure a real secret key. Using the default key would allow attackers to
    forge authentication JWT tokens.

    Solution:
    A Pydantic model validator checks the active environment:
    - In 'development': Accepts the default insecure key for developer convenience.
    - In 'staging' / 'production': Raises a ValueError if the key is the default or <32 chars.
    """
    default_insecure_key = "dev-only-insecure-secret-change-me"
    secure_staging_key = "a_very_secure_production_key_with_at_least_32_characters!"

    # Sub-case A: Local development allows the default key so developers don't have to configure secrets
    dev_settings = Settings(environment="development", secret_key=default_insecure_key)
    assert dev_settings.secret_key == default_insecure_key

    # Sub-case B: Staging environment strictly REJECTS the default developer key
    with pytest.raises(ValueError, match="CRITICAL SECURITY INVARIANT VIOLATION"):
        Settings(environment="staging", secret_key=default_insecure_key)

    # Sub-case C: Production environment strictly REJECTS the default developer key
    with pytest.raises(ValueError, match="CRITICAL SECURITY INVARIANT VIOLATION"):
        Settings(environment="production", secret_key=default_insecure_key)

    # Sub-case D: Staging environment REJECTS weak/short keys (< 32 characters / 256 bits)
    with pytest.raises(ValueError, match="CRITICAL SECURITY INVARIANT VIOLATION"):
        Settings(environment="staging", secret_key="short_16_char_key!")

    # Sub-case E: Staging environment ACCEPTS strong 32+ character key
    staging_settings = Settings(environment="staging", secret_key=secure_staging_key)
    assert staging_settings.secret_key == secure_staging_key


def test_INF_4_0_2_criterion_4_connection_pooling_and_check_diagnostic(db_session):
    """
    Acceptance Criterion 4: Connection Pooling & Socket Liveness Probe.

    Problem in C++ / Systems terms:
    Opening TCP sockets, performing TLS handshakes, and authenticating on every HTTP
    request introduces massive latency (50-200ms per request).
    An Object Pool pattern (Connection Pool) keeps a set of open sockets in memory.

    Solution:
    Settings exposes pool sizing (db_pool_size, db_max_overflow, db_pool_pre_ping).
    The check_database_connection helper executes a lightweight 'SELECT 1' over an
    active session and measures round-trip latency using high-resolution time.perf_counter().
    """
    s = Settings()
    assert s.db_pool_size >= 1
    assert s.db_max_overflow >= 0
    assert s.db_pool_timeout > 0
    assert s.db_pool_pre_ping is True

    # Run the liveness probe against the active test database session
    diag = check_database_connection(db_session)
    assert diag["status"] == "ok"
    assert diag["database"] == "connected"
    assert "dialect" in diag
    assert isinstance(diag["latency_ms"], float)
    assert diag["latency_ms"] >= 0.0


def test_INF_4_0_2_criterion_5_health_db_endpoint_success(client: TestClient):
    """
    Acceptance Criterion 5: GET /api/health/db Success Verification.

    Verifies the HTTP endpoint that cloud orchestrators (Kubernetes, AWS ECS, Docker)
    use as a liveness and readiness probe.
    Returns HTTP 200 with connection status and latency when the database is healthy.
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
    Acceptance Criterion 6: Fault-Tolerance & Dropped Socket Handling.

    Problem in C++ / Systems terms:
    If the remote database restarts or the network wire is severed, the backend must
    not crash the entire web process. It must catch the socket exception, report an
    appropriate HTTP 503 Service Unavailable code, and return diagnostic error details.

    Solution:
    Using unittest.mock.patch, we simulate a dropped connection. The endpoint catches
    the error and gracefully returns HTTP 503 without throwing an unhandled 500 panic.
    """
    with patch("app.main.check_database_connection", side_effect=Exception("Database socket connection timed out")):
        response = client.get("/api/health/db")
        assert response.status_code == 503

        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
        assert "Database socket connection timed out" in data["error"]
