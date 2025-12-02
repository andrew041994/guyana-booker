import os
from functools import lru_cache
from typing import List
from dotenv import load_dotenv, find_dotenv

# Load the nearest .env file (root .env or backend/.env)
load_dotenv(find_dotenv(), override=False)

class Settings:
    """Application configuration loaded from environment variables.

    This keeps environment-specific behavior (dev/test/prod) and security-
    sensitive values (JWT secret, DB URL, CORS) in one place.
    """

    def __init__(self) -> None:
    # Environment: dev, test, prod
        self.ENV: str = os.getenv("ENV", "dev").lower()

        # NEW logging level
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Database – 🔥 no more SQLite default allowed
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError(
                "DATABASE_URL is not set. "
                "Set it to your PostgreSQL URL, e.g. "
                "postgresql+psycopg2://postgres:postgres@localhost:8001/postgres"
            )
        self.DATABASE_URL: str = db_url

    # -----------------------------
    # 🔐 AUTH / JWT — STRONG SECRET REQUIRED IN PROD
    # -----------------------------
               # Auth / JWT
        legacy_secret = os.getenv("JWT_SECRET")
        env_secret = os.getenv("JWT_SECRET_KEY") or legacy_secret

        if self.ENV == "dev":
            # Dev is allowed to fall back to a weak default for convenience
            self.JWT_SECRET_KEY: str = env_secret or "dev-secret"
        else:
            # Any non-dev environment MUST have a strong secret
            if not env_secret or len(env_secret) < 32:
                raise RuntimeError(
                    "JWT secret is not set or is too weak for non-dev environment. "
                    "Set JWT_SECRET_KEY (or legacy JWT_SECRET) to a strong value "
                    "at least 32 characters long."
                )
            self.JWT_SECRET_KEY: str = env_secret


        # -----------------------------
        # 🌐 CORS — EXPLICIT ORIGINS ONLY
        # -----------------------------
                # CORS
        raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "")

        if raw_origins:
            parsed_origins = [
                origin.strip()
                for origin in raw_origins.split(",")
                if origin.strip()
            ]

            # Disallow wildcard CORS in any non-dev environment
            if any(o == "*" for o in parsed_origins) and self.ENV != "dev":
                raise RuntimeError(
                    "CORS_ALLOW_ORIGINS cannot contain '*' when ENV is not 'dev'. "
                    "Use explicit origins instead."
                )
        else:
            # Explicit safe defaults for dev/test
            if self.ENV in ("dev", "test"):
                parsed_origins = [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:19006",
                    "http://127.0.0.1:19006",
                ]
            else:
                # In prod/other, missing CORS config is an error
                raise RuntimeError(
                    "CORS_ALLOW_ORIGINS is not set for this environment. "
                    "Set it to a comma-separated list of allowed origins."
                )

        self.CORS_ALLOW_ORIGINS: List[str] = parsed_origins

        # Demo data seeding – OFF by default, must be explicitly enabled
        self.ENABLE_DEMO_SEED: bool = (
            os.getenv("ENABLE_DEMO_SEED", "false").lower() == "true"
        )


        # -----------------------------
        # Cloudinary
        # -----------------------------
        self.CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
        self.CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
        self.CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
        self.CLOUDINARY_UPLOAD_FOLDER: str = os.getenv(
        "CLOUDINARY_UPLOAD_FOLDER", "bookitgy/avatars"
    )




@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
