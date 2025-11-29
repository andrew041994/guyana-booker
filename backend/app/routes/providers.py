from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas, models
from app.security import get_current_user_from_header

router = APIRouter(tags=["providers"])


# -------------------------------------------------------------------
# Provider "me" profile
# -------------------------------------------------------------------

@router.get("/providers/me")
def get_my_provider(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.put("/providers/me")
def update_my_provider(
    provider_update: schemas.ProviderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    updated = crud.update_provider(db, provider.id, provider_update)
    return updated


# -------------------------------------------------------------------
# Provider "me" services
# -------------------------------------------------------------------

@router.get("/providers/me/services")
def list_my_services(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    return crud.list_services_for_provider(db, provider.id)


@router.post("/providers/me/services")
def create_my_service(
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    return crud.create_service_for_provider(db, provider.id, service_in)


@router.put("/providers/me/services/{service_id}")
def update_my_service(
    service_id: int,
    service_update: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    return crud.update_service(db, provider.id, service_id, service_update)


@router.delete("/providers/me/services/{service_id}")
def delete_my_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    crud.delete_service(db, provider.id, service_id)
    return {"status": "deleted"}


# -------------------------------------------------------------------
# Provider "me" working-hours + summary
# -------------------------------------------------------------------

@router.get("/providers/me/working-hours", response_model=List[schemas.WorkingHoursOut])
def get_my_working_hours(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    """
    Return 7 rows (Mon–Sun). If none exist, create defaults (all closed)
    so the frontend always has something to render.
    """
    provider = crud.get_or_create_provider_for_user(db, current_user.id)
    return crud.get_or_create_working_hours_for_provider(db, provider.id)


@router.put(
    "/providers/me/working-hours",
    response_model=List[schemas.WorkingHoursOut],
)
def update_my_working_hours(
    hours: List[schemas.ProviderWorkingHoursUpdate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    """
    Replace this provider's working hours with the given list.
    Each item should have: weekday, is_closed, start_time, end_time.
    """
    provider = crud.get_or_create_provider_for_user(db, current_user.id)

    # Convert Pydantic models -> plain dicts for the CRUD helper
    rows = crud.set_working_hours_for_provider(
        db=db,
        provider_id=provider.id,
        hours_list=[h.model_dump() for h in hours],
    )
    return rows


@router.get("/providers/me/summary")
def get_my_provider_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)

    # You can wire this to real fee logic if desired:
    # fees_due = crud.get_provider_fees_due(db, provider.id)
    total_fees_due = 0

    return {
        "account_number": provider.account_number,
        "total_fees_due_gyd": float(total_fees_due or 0.0),
    }


# -------------------------------------------------------------------
# Public provider routes
# -------------------------------------------------------------------

@router.get("/providers")
def list_providers(
    profession: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.list_providers(db, profession=profession)


@router.get("/providers/{provider_id}")
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = crud.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.get("/providers/{provider_id}/services")
def list_provider_services(provider_id: int, db: Session = Depends(get_db)):
    return crud.list_services_for_provider(db, provider_id)

@router.get(
    "/providers/{provider_id}/availability",
    response_model=List[schemas.ProviderAvailabilityDay],
)
def get_provider_availability_route(
    provider_id: int,
    service_id: int,
    days: int = 14,
    db: Session = Depends(get_db),
):
    """
    Availability for a specific provider + service over the next `days`.
    Used by the client calendar/time slot picker.
    """
    try:
        availability = crud.get_provider_availability(
            db,
            provider_id=provider_id,
            service_id=service_id,
            days=days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return availability


@router.put("/providers/me")
def update_my_provider_location(
    payload: schemas.ProviderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    provider = crud.get_or_create_provider_for_user(db, current_user.id)

    # Only update lat/long if provided
    if payload.lat is not None:
        provider.lat = payload.lat
    if payload.long is not None:
        provider.long = payload.long

    db.commit()
    db.refresh(provider)
    return provider
