from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app import crud, models

settings = get_settings()


def get_current_user_from_header(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> models.User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token in Authorization header",
        )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = crud.get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
