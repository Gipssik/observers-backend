import re

from sqlalchemy.orm import Session

from database.crud import get_object_by_expression
from database import models


def isemail(email: str):
    return re.fullmatch(r'^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$', email)


def get_user_by_username_or_email(db: Session, username: str) -> models.User | None:
    """Returns a `User` object if `username` equals User's username or email. Otherwise `None`.

    Returns:
        `models.User | None`: A `User` object if `username` equals User's username or email. Otherwise `None`.
    """

    return get_object_by_expression(cls=models.User, db=db, expression=(models.User.email == username)) \
        if isemail(username) \
        else get_object_by_expression(cls=models.User, db=db, expression=(models.User.username == username))
