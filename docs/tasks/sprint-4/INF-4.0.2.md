---
id: INF-4.0.2
story: INF-4.0
sprint: 4
assignee: John Weaver
estimate_hours: 4
---

# Configure Staging Cloud Database Instance, SSL Connection Strings, and Secure Environment Secret Injection

## Description
Serves **INF-4.0** (*Production Staging Deployment*). With container configurations established in Task INF-4.0.1, the Simmer application requires cloud database connectivity and secure configuration management for staging deployment.

In local development, the backend defaults to an unencrypted, file-based SQLite database (`sqlite:///./simmer.db`) with a default insecure development secret key. In cloud staging (e.g., AWS RDS, Neon, Supabase, Render PostgreSQL), database connections operate over TCP sockets requiring:
1. Robust database URL parsing that normalizes legacy cloud `postgres://` prefixes to modern SQLAlchemy `postgresql://` or `postgresql+psycopg2://`.
2. Encrypted transport enforcement via SSL connection modes (`sslmode=require`).
3. Connection pooling (object pooling) with automatic pre-ping (`pool_pre_ping=True`) to recycle dropped cloud socket connections.
4. Environment-aware secret injection with strict validation: when running in `staging` or `production`, the application refuses to start if the default insecure secret key is detected.
5. A database liveness and latency inspection endpoint (`GET /api/health/db`) for staging smoke tests and orchestrator probes.

## Specs
- **Configuration Management (`backend/app/core/config.py`):**
  - `environment`: String representing current environment (`Literal["development", "staging", "production", "test"]`, default: `"development"`).
  - `database_url`: String database connection URI. Implements validator/property `normalized_database_url` that converts legacy `postgres://` or `postgresql://` prefixes to `postgresql+psycopg2://` (or `postgresql://`) and injects/verifies SSL parameters when configured.
  - `db_ssl_mode`: Optional string (default: `"require"` in staging/production, `None` for local SQLite).
  - `db_pool_size`: Integer connection pool size (default: `5`, max overflow: `10`).
  - `db_pool_pre_ping`: Boolean (default: `True`) enabling socket liveness check prior to checkout.
  - `db_pool_timeout`: Integer seconds to wait for a connection from the pool (default: `30`).
  - `secret_key`: Validates that if `environment` is `"staging"` or `"production"`, `secret_key` must NOT equal the default `"dev-only-insecure-secret-change-me"` and must be at least 32 characters in length.

- **Database Engine & Connection Pooling (`backend/app/core/database.py`):**
  - Instantiates SQLAlchemy `create_engine` with `pool_pre_ping=True`.
  - For non-SQLite dialects (PostgreSQL), configures `pool_size`, `max_overflow`, and `pool_timeout`.
  - Exposes `check_database_connection(db: Session)` utility executing `SELECT 1` and measuring response latency in milliseconds.

- **Staging Database Health Check Endpoint (`GET /api/health/db` in `backend/app/main.py`):**
  - Public endpoint returning database connection health details.
  - On success: Returns HTTP 200 with `{ "status": "ok", "database": "connected", "dialect": "<dialect>", "latency_ms": <float> }`.
  - On connection error: Returns HTTP 503 Service Unavailable with `{ "status": "unhealthy", "database": "disconnected", "error": "<reason>" }`.

## Requirements
- Maintain 100% backward compatibility for local SQLite development without breaking existing developers' workflows.
- Strictly adhere to Pydantic v2 / `pydantic-settings` validation patterns.
- Guard against security vulnerabilities by preventing default secrets in staging/production.
- Provide clear, beginner-friendly comments throughout all code changes explaining database connection pools, SSL flags, and URL normalization.
- Write automated verification tests in `backend/tests/test_INF_4_0_2.py`.
- Zero regressions across the existing backend test suite.

## Acceptance criteria
1. `Settings` accurately normalizes cloud PostgreSQL URLs starting with `postgres://` to `postgresql://` (or driver-specific variant).
2. When `db_ssl_mode` is set (e.g. `require`), the normalized database URL ensures SSL query arguments (`sslmode=require`) are appropriately appended for PostgreSQL connections.
3. In `staging` or `production` environment modes, attempting to initialize settings with the default insecure secret key or an insecure key (<32 characters) raises a `ValueError` validation error.
4. Database engine initialization applies connection pooling configuration (`pool_pre_ping=True`, `pool_size`, `max_overflow`) for non-SQLite databases.
5. The `GET /api/health/db` endpoint executes a lightweight query (`SELECT 1`), confirms database responsiveness, and returns HTTP 200 with latency and dialect metadata.
6. The `GET /api/health/db` endpoint returns HTTP 503 with informative diagnostic JSON if the database connection fails.
7. Automated tests in `backend/tests/test_INF_4_0_2.py` validate all URL normalization, SSL injection, secret validation, pooling, and health endpoint criteria with 100% pass rate.
