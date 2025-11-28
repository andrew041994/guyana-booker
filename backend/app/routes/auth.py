from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app import crud, schemas

router = APIRouter(tags=["auth"])
settings = get_settings()


@router.post("/auth/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    created = crud.create_user(db, user)
    return created


def _create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


@router.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Form-style login:
    - username: email
    - password: password
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = _create_access_token(user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "is_provider": user.is_provider,
    }


@router.post("/auth/login_by_email")
def login_by_email(
    payload: schemas.LoginByEmailPayload,
    db: Session = Depends(get_db),
):
    """
    JSON-style login:
    {
      "email": "...",
      "password": "..."
    }
    """
    user = crud.authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = _create_access_token(user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "is_provider": user.is_provider,
    }
