from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables or backend/.env."""

    database_url: str = "sqlite:///./simmer.db"
    secret_key: str = "dev-only-insecure-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # US4.3.2: Initial tunable discovery policy, not fixed constants in query logic.
    # Defaults are a starting policy for review; environment variables can override them.
    trending_like_weight: float = Field(default=3.0, ge=0, allow_inf_nan=False)
    trending_comment_weight: float = Field(default=5.0, ge=0, allow_inf_nan=False)
    trending_completion_weight: float = Field(default=4.0, ge=0, allow_inf_nan=False)
    trending_window_days: int = Field(default=7, ge=1)
    trending_decay_hours: float = Field(default=24.0, gt=0, allow_inf_nan=False)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
