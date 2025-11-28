import os
from functools import lru_cache
from typing import List


class Settings:
    """Application configuration loaded from environment variables.

    This keeps environment-specific behavior (dev/test/prod) and security-
    sensitive values (JWT secret, DB URL, CORS) in one place.
    """

    def __init__(self) -> None:
        # Environment: dev, test, prod
        self.ENV: str = os.getenv("ENV", "dev").lower()

        # NEW logging level (this is all you add)
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

        # Auth / JWT
        # Prefer JWT_SECRET_KEY but fall back to legacy JWT_SECRET if set
        legacy_secret = os.getenv("JWT_SECRET")
        self.JWT_SECRET_KEY: str = (
            os.getenv("JWT_SECRET_KEY") or legacy_secret or "dev-secret"
        )
        self.JWT_ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )

        # CORS
        # Provide a comma-separated list of allowed origins, e.g.:
        # CORS_ALLOW_ORIGINS=https://bookitgy.com,https://app.bookitgy.com
        raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
        self.CORS_ALLOW_ORIGINS: List[str] = [
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        ]

        # Demo data seeding
        # Enable only in development by default
        self.ENABLE_DEMO_SEED: bool = (
            os.getenv("ENABLE_DEMO_SEED", "true").lower() == "true"
        )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using a cache avoids re-reading environment variables on every import.
    """
    return Settings()
