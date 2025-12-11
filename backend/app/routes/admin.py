from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.security import get_current_user_from_header

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: models.User = Depends(get_current_user_from_header)) -> models.User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/service-charge", response_model=schemas.ServiceChargeOut)
def get_service_charge(
    db: Session = Depends(get_db),
    _: models.User = Depends(_require_admin),
):
    pct = crud.get_platform_service_charge_percentage(db)
    return {"service_charge_percentage": float(pct)}


@router.put("/service-charge", response_model=schemas.ServiceChargeOut)
def update_service_charge(
    payload: schemas.ServiceChargeUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(_require_admin),
):
    pct = crud.update_platform_service_charge(db, payload.service_charge_percentage)
    return {"service_charge_percentage": float(pct)}


@router.put(
    "/promotions/{account_number}",
    response_model=schemas.BillCreditOut,
)
def apply_bill_credit(
    account_number: str,
    payload: schemas.BillCreditUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(_require_admin),
):
    provider = (
        db.query(models.Provider)
        .filter(models.Provider.account_number == account_number)
        .first()
    )

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    credit = crud.create_bill_credit(db, provider.id, payload.credit_gyd)
    balance = crud.get_provider_credit_balance(db, provider.id)

    return {
        "provider_id": provider.id,
        "account_number": provider.account_number,
        "credit_applied_gyd": float(credit.amount_gyd or 0.0),
        "total_credit_balance_gyd": float(balance or 0.0),
    }
