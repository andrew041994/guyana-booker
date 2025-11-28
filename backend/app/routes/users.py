from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas, models
from app.security import get_current_user_from_header

router = APIRouter(tags=["users"])


@router.get("/users/me")
def read_users_me(
    current_user: models.User = Depends(get_current_user_from_header),
):
    return current_user


@router.put("/users/me")
def update_users_me(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_header),
):
    updated_user = crud.update_user(db, current_user.id, user_update)
    return updated_user
