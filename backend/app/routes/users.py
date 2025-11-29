from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import traceback
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
    """
    Partially update the current user.
    Only fields that are actually sent by the client are changed.
    """
    try:
        updated_user = crud.update_user(db, current_user.id, user_update)
    except SQLAlchemyError as e:
        # This will show up in `docker compose logs backend`
        print("ERROR updating user in /users/me:", repr(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating user profile.",
        )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user

