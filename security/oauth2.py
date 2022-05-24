from sqlalchemy.orm import Session

from database import models

from . import hashing

from services import get_user_by_username_or_email


async def authenticate_user(db: Session, username: str, password: str) -> models.User | bool:
    """Returns a user with `username` and `password` if exists, otherwise returns `False`.

    Returns:
        `models.User` | `bool`: `models.User` object if exists, otherwise `False`.
    """

    user = get_user_by_username_or_email(db=db, username=username)
    if not user:
        return False
    if not await hashing.verify_password(password, user.password):
        return False
    return user



