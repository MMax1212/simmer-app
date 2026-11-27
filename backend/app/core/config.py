"""
backend/app/core/config.py — Application Configuration & Cloud Staging Secret Management
========================================================================================
Architectural Context (INF-4.0.2):
In C++ and systems programming, configuring network services requires managing:
  1. Socket endpoints (host, port, protocol)
  2. Transport layer security (TLS/SSL encryption handshakes)
  3. Object pooling (reusing TCP socket connections instead of expensive reconnections)
  4. Environment-gated invariants (asserting strong cryptographic keys in staging/production)

This module uses Pydantic Settings to load and validate these parameters from
environment variables, OS secrets, or local `.env` files.
========================================================================================
"""

from typing import Literal
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Simmer Configuration Class.
    Reads environment variables (case-insensitive) or backend/.env fallback.
    """

    # --------------------------------------------------------------------------
    # Environment Mode
    # --------------------------------------------------------------------------
    # Controls runtime strictness: development, staging, production, or test.
    environment: Literal["development", "staging", "production", "test"] = "development"

    # --------------------------------------------------------------------------
    # Database Connection URI & Pooling Configuration
    # --------------------------------------------------------------------------
    # Default is local SQLite for developer ease.
    # Cloud staging instances (AWS RDS, Neon, Supabase, Render) provide PostgreSQL URIs.
    database_url: str = "sqlite:///./simmer.db"

    # Cloud PostgreSQL SSL Mode:
    # "require" forces encrypted TLS transport over open internet TCP connections.
    # Left as None for local SQLite file connections.
    db_ssl_mode: str | None = None

    # Connection Pooling (C++ Object Pool Pattern):
    # Instead of tearing down and recreating TCP sockets on every HTTP request,
    # SQLAlchemy maintains a persistent pool of open connections.
    # - db_pool_size: Base number of persistent connections kept open in the pool.
    # - db_max_overflow: Maximum additional burst connections allowed under high load.
    # - db_pool_timeout: Maximum seconds an API worker thread will wait for a free connection.
    # - db_pool_pre_ping: Liveness probe ("SELECT 1") before checkout to discard dead sockets.
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_pre_ping: bool = True

    # --------------------------------------------------------------------------
    # Cryptographic Authentication & Token Secrets
    # --------------------------------------------------------------------------
    # Used by PyJWT to sign and verify HMAC-SHA256 authentication tokens.
    secret_key: str = "dev-only-insecure-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # --------------------------------------------------------------------------
    # Cross-Origin Resource Sharing (CORS)
    # --------------------------------------------------------------------------
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:80",
        "http://localhost",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    # --------------------------------------------------------------------------
    # URL Normalization & SSL Transport Injection
    # --------------------------------------------------------------------------
    @property
    def normalized_database_url(self) -> str:
        """
        Normalizes database URLs for cloud staging compatibility:
        1. Cloud providers (e.g. Heroku, AWS, Render) often emit legacy 'postgres://' URLs.
           SQLAlchemy 2.0 requires 'postgresql://' (or dialect driver 'postgresql+psycopg2://').
        2. Injects 'sslmode=<mode>' query parameters for PostgreSQL connections if configured.
        """
        url = self.database_url.strip()

        # Fix legacy postgres:// dialect prefix
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        # For SQLite connections, SSL query arguments are not applicable
        if url.startswith("sqlite"):
            return url

        # If SSL mode is specified (e.g. "require") and connection is PostgreSQL,
        # ensure sslmode is present in query string parameters.
        if self.db_ssl_mode and url.startswith("postgresql"):
            parsed = urlparse(url)
            query_params = dict(parse_qsl(parsed.query))
            if "sslmode" not in query_params:
                query_params["sslmode"] = self.db_ssl_mode
                new_query = urlencode(query_params)
                url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment,
                ))

        return url

    # --------------------------------------------------------------------------
    # Security Invariant Enforcement
    # --------------------------------------------------------------------------
    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """
        Prevents critical deployment vulnerabilities:
        In staging and production environments, the service will refuse to boot
        if the insecure developer default secret key is still in use, or if the
        key provides insufficient cryptographic entropy (< 32 characters).
        """
        is_cloud_env = self.environment in ("staging", "production")

        if is_cloud_env:
            default_dev_key = "dev-only-insecure-secret-change-me"
            if self.secret_key == default_dev_key:
                raise ValueError(
                    f"CRITICAL SECURITY INVARIANT VIOLATION: Environment is '{self.environment}', "
                    "but 'secret_key' is set to the default development key. "
                    "A secure, randomly generated 256-bit secret is required."
                )
            if len(self.secret_key) < 32:
                raise ValueError(
                    f"CRITICAL SECURITY INVARIANT VIOLATION: Environment is '{self.environment}', "
                    f"but 'secret_key' length is only {len(self.secret_key)} characters. "
                    "Minimum required length is 32 characters for HMAC-SHA256."
                )

        return self


# Global singleton settings instance used across backend
settings = Settings()
