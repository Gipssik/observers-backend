from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import get_db
from .oauth2 import authenticate_user
from . import security_token
from .schemas import Token

router = APIRouter(tags=['security'])


@router.post("/api/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    """Returns a `dict` with token and its type.

    Args:
        `form_data` (OAuth2PasswordRequestForm, optional): `OAuth2PasswordRequestForm` form.
        `db` (Session, optional): Database connection.

    Raises:
        `HTTPException`: If incorrect credentials were given.

    Returns:
        `dict`: A `dict` with token and its type.
    """

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security_token.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security_token.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
