"""One-off helper to initialize the database schema.

Usage:

    # From the backend directory:
    #   python3 -m app.init_db

This script explicitly creates the tables using SQLAlchemy metadata.
It replaces the old approach where tables were created automatically
just by importing models. This is safer and gives you control.
"""

from .database import Base, engine  # <-- relative import inside app package
from app import models  # Ensure all models are registered on Base.metadata


def init_db() -> None:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")


if __name__ == "__main__":
    init_db()
