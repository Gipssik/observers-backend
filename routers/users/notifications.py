from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import crud, schemas, models
from dependencies import get_db, get_current_user
from decorators import raise_403_if_not_admin, raise_403_if_no_access


router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('/', response_model=list[schemas.Notification])
@raise_403_if_not_admin
def get_notifications(
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> list[models.Notification]:
    """Gets all `Notifications` from database in range [`skip`:`skip+limit`] and returns them to the client.

    Args:
        `skip` (Optional[int], optional): How many objects to skip. Defaults to 0.
        `limit` (Optional[int], optional): Maximum amount of objects. Defaults to 100.
        `db` (Session, optional): Database connection.

    Returns:
        list[models.Notification]: A `list` of all `Notification` objects.
    """

    return crud.get_objects(cls=models.Notification, db=db, skip=skip, limit=limit)


@router.post('/', response_model=schemas.Notification)
@raise_403_if_not_admin
def create_notification(
        notification: schemas.NotificationCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Notification:
    """Creates a `Notification` object with a given `notification` schema.

    Args:
        `notification` (schemas.NotificationCreate): A `schemas.NotificationCreate` object.
        `db` (Session, optional): [description]. Database connection.

    Returns:
        `models.Notification`: A new `Notification` object.
    """

    return crud.create_notification(db=db, notification=notification)


@router.get('/{user_id}/', response_model=list[schemas.Notification])
@raise_403_if_no_access
def get_user_notifications(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> list[models.Notification]:
    """Gets notifications by a given `user_id` in range[`skip`:`skip+limit`] and returns them to the client.

    Args:
        `user_id` (int): `User` object id.
        `skip` (int, optional): How many objects to skip. Defaults to 0.
        `limit` (int, optional): Maximum amount of objects. Defaults to 100.
        `db` (Session, optional): Database connection.

    Returns:
        `list[models.Notification]`: A list of `Notification` objects.
    """
    
    return crud.get_notifications_by_user_id(db=db, user_id=user_id, skip=skip, limit=limit)


@router.delete('/{notification_id}/')
def delete_notification(
        notification_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> Response:
    """Deletes a notification by a given `notification_id`.

    Args:
        `notification_id` (int): `Notification`'s id.
        `db` (Session, optional): Database connection.

    Returns:
        `Response`: No content response.
    """

    notification = crud.get_object(cls=models.Notification, db=db, object_id=notification_id)
    if notification.user_id != current_user.id and current_user.role.title != 'Admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not that user.'
        )

    crud.delete_object(cls=models.Notification, db=db, object_id=notification_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch('/{notification_id}/', response_model=schemas.Notification)
@raise_403_if_not_admin
def update_notification(
        notification_id: int,
        notification: schemas.NotificationUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Notification:
    """Updates `Notification` object by given `notification_id` and `notification` schema and returns it.

    Args:
        `notification_id` (int): `Notification` object's id.
        `notification` (schemas.UserUpdate): Pydantic notification schema.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Notification`: Updated `Notification` object.
    """

    return crud.update_object(
        cls=models.Notification,
        db=db,
        object_id=notification_id,
        schema_object=notification
    )
