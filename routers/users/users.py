from typing import Optional, Union
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import crud, schemas, models
from dependencies import get_current_user, get_db
from decorators import raise_403_if_not_admin, raise_403_if_no_access
from services import isemail

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
    """Creates a `User` object with a given `user` schema and returns it to the client.

    Args:
        `user` (schemas.UserCreate): A `schemas.UserCreate` object.
        `db` (Session, optional): Database connection.

    Returns:
        `models.User`: A new `User` object.
    """

    return crud.create_user(db=db, user=user)


@router.get('/', response_model=list[schemas.User])
def get_users(skip: Optional[int] = 0, limit: Optional[int] = 100, db: Session = Depends(get_db)) -> list[models.User]:
    """Gets all `Users` from database in range [`skip`:`skip+limit`] and returns them to the client.

    Args:
        `skip` (Optional[int], optional): How many objects to skip. Defaults to 0.
        `limit` (Optional[int], optional): Maximum amount of objects. Defaults to 100.
        `db` (Session, optional): Database connection.

    Returns:
        `list[models.User]`: A `list` of all `User` objects.
    """

    return crud.get_objects(cls=models.User, db=db, skip=skip, limit=limit)


@router.get("/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)) -> models.User:
    """Returns a `current_user`.

    Args:
        `current_user` (schemas.User, optional): A `schemas.User` object of current user.

    Returns:
        `models.User`: A `schemas.User` object of current user.
    """

    return current_user


@router.get('/{user_key}/', response_model=schemas.User)
def get_user(user_key: Union[int, str], db: Session = Depends(get_db)) -> models.User:
    """Gets a `User` object from the database by `role_key` and returns it to the client.

    Args:
        `role_key` (int): A `User` object id, username or email.
        `db` (Session, optional): Database connection.

    Raises:
        `HTTPException`: If an invalid `user_key` was given.

    Returns:
        `models.User`: A new `User` object.
    """

    if isinstance(user_key, int):
        return crud.get_object(cls=models.User, db=db, object_id=user_key)
    elif isemail(user_key):
        return crud.get_object_by_expression(
            cls=models.User,
            db=db,
            expression=(models.User.email == user_key)
        )
    elif user_key.replace('_', '').isalnum():
        return crud.get_object_by_expression(
            cls=models.User,
            db=db,
            expression=(models.User.username == user_key),
            raise_404=True
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Unresolved user_key.'
    )


@router.delete('/{user_id}/')
@raise_403_if_no_access
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> Response:
    """Deletes a user by a given `user_id`.

    Args:
        `user_id` (int): `User`'s id.
        `db` (Session, optional): Database connection.
        `current_user` (schemas.User, optional): A `schemas.User` object of current user.

    Returns:
        `Response`: No content response.
    """

    crud.delete_object(cls=models.User, db=db, object_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch('/{user_id}/', response_model=schemas.User)
@raise_403_if_no_access
def update_user(
        user_id: int,
        user: schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.User:
    """Updates `User` object by given `user_id` and `user` schema and returns it.

    Args:
        `user_id` (int): `User` object's id.
        `user` (schemas.UserUpdate): Pydantic user schema.
        `db` (Session, optional): Database connection.
        `current_user` (schemas.User, optional): A `schemas.User` object of current user.

    Returns:
        `models.User`: Updated `User` object.
    """

    return crud.update_user(db=db, user_id=user_id, user=user)
