import os
from typing import Dict, Any

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.database import get_db, SessionLocal
from app import crud, schemas, models
from app.routes import auth as auth_routes
from app.routes import users as users_routes
from app.routes import providers as providers_routes
from app.routes import bookings as bookings_routes
from app.routes import profile as profile_routes
from app.security import get_current_user_from_header
from app.workers.cron import registerCronJobs

settings = get_settings()

app = FastAPI(title="Guyana Booker")
scheduler = BackgroundScheduler()


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
allow_origins = settings.CORS_ALLOW_ORIGINS or []
if not allow_origins:
    raise RuntimeError(
        "CORS_ALLOW_ORIGINS is empty. "
        "Set it in your environment to a comma-separated list of allowed origins."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Scheduler / Cron jobs
# -------------------------------------------------------------------
def start_scheduler() -> None:
    """Start the background scheduler and register cron jobs (only once)."""
    if scheduler.running:
        return

    registerCronJobs(scheduler)
    scheduler.start()


# -------------------------------------------------------------------
# Demo data seeding
# -------------------------------------------------------------------
def _seed_demo_users() -> None:
    """Seed demo users in development environment only."""
    if not settings.ENABLE_DEMO_SEED or settings.ENV != "dev":
        return

    db: Session = SessionLocal()
    try:
        # Customer
        if not crud.get_user_by_email(db, "customer@guyana.com"):
            crud.create_user(
                db,
                schemas.UserCreate(
                    email="customer@guyana.com",
                    password="pass",
                    full_name="Demo Customer",
                ),
            )

        # Provider
        if not crud.get_user_by_email(db, "provider@guyana.com"):
            user = crud.create_user(
                db,
                schemas.UserCreate(
                    email="provider@guyana.com",
                    password="pass",
                    full_name="Demo Provider",
                ),
            )
            crud.get_or_create_provider_for_user(db, user.id)
    finally:
        db.close()


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
app.include_router(auth_routes.router)
app.include_router(users_routes.router)
app.include_router(providers_routes.router)
app.include_router(bookings_routes.router)
app.include_router(profile_routes.router)


# -------------------------------------------------------------------
# Provider location endpoint (restricted & validated)
# -------------------------------------------------------------------
@app.put("/providers/me/location")
def update_my_location(
    payload: Dict[str, Any],
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Allow a *provider* to update their public location (lat/long + optional text).

    - Only works for users who are providers.
    - Validates latitude/longitude bounds.
    """
    user = get_current_user_from_header(authorization, db)

    if not getattr(user, "is_provider", False):
        raise HTTPException(
            status_code=403,
            detail="Only providers can update their pinned location.",
        )

    lat = payload.get("lat")
    long = payload.get("long")
    location = payload.get("location")  # optional

    if lat is None or long is None:
        raise HTTPException(status_code=400, detail="lat and long are required")

    # Parse & validate
    try:
        lat_f = float(lat)
        long_f = float(long)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="lat and long must be numeric values",
        )

    if not (-90.0 <= lat_f <= 90.0):
        raise HTTPException(
            status_code=400,
            detail="lat must be between -90 and 90 degrees",
        )
    if not (-180.0 <= long_f <= 180.0):
        raise HTTPException(
            status_code=400,
            detail="long must be between -180 and 180 degrees",
        )

    user.lat = lat_f
    user.long = long_f
    if location is not None:
        user.location = location

    db.commit()
    db.refresh(user)

    return {
        "status": "updated",
        "lat": user.lat,
        "long": user.long,
        "location": user.location,
    }


# -------------------------------------------------------------------
# Startup hook
# -------------------------------------------------------------------
@app.on_event("startup")
def on_startup() -> None:
    _seed_demo_users()
    start_scheduler()
