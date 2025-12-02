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
        legacy_secret = os.getenv("JWT_SECRET")
        env_secret = os.getenv("JWT_SECRET_KEY") or legacy_secret

        if self.ENV == "prod":
            # Require a strong secret
            if not env_secret or len(env_secret) < 32:
                raise RuntimeError(
                    "JWT secret missing or too weak for production. "
                    "Set JWT_SECRET_KEY (or legacy JWT_SECRET) to a strong value."
                )
            self.JWT_SECRET_KEY = env_secret
        else:
            # Dev/test fallback allowed
            self.JWT_SECRET_KEY = env_secret or "dev-secret"

            self.JWT_ALGORITHM: str = "HS256"
            self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )

        # -----------------------------
        # 🌐 CORS — EXPLICIT ORIGINS ONLY
        # -----------------------------
        raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "")

        if raw_origins:
            parsed = [o.strip() for o in raw_origins.split(",") if o.strip()]
        else:
            if self.ENV == "prod":
                raise RuntimeError(
                    "CORS_ALLOW_ORIGINS is required in production "
                    "and must contain one or more allowed origins."
                )
            # Dev defaults — safe localhost list (NO WILDCARD)
            parsed = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:19006",
                "http://127.0.0.1:19006",
            ]

        self.CORS_ALLOW_ORIGINS: List[str] = parsed

        # -----------------------------
        # Demo seeding
        # -----------------------------
        self.ENABLE_DEMO_SEED: bool = (
            os.getenv("ENABLE_DEMO_SEED", "true").lower() == "true"
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
