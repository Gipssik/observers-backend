from typing import Union
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm.session import Session

from database import crud, models, schemas
from dependencies import get_db, get_current_user
from decorators import raise_403_if_not_admin

router = APIRouter(prefix='/tags', tags=['tags'])


@router.post('/', response_model=schemas.Tag)
@raise_403_if_not_admin
def create_tag(
        tag: schemas.TagCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Tag:
    """Creates a `Tag` object with a given `TagCreate` schema.

    Args:
        `tag` (schemas.TagCreate): A `schemas.TagCreate` object.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Tag`: `Tag` object.
    """

    return crud.create_tag(db=db, tag=tag)


@router.get('/', response_model=list[schemas.Tag])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[models.Tag]:
    """Gets all `Tags` from database in range [`skip`:`skip+limit`] and returns them to the client.

    Args:
        `skip` (Optional[int], optional): How many objects to skip. Defaults to 0.
        `limit` (Optional[int], optional): Maximum amount of objects. Defaults to 100.
        `db` (Session, optional): Database connection.

    Returns:
        `list[models.Tag]`: A `list` of all `Tag` objects.
    """

    return crud.get_objects(cls=models.Tag, db=db, skip=skip, limit=limit)


@router.get('/{tag_key}/', response_model=schemas.Tag)
def get_tag(tag_key: Union[int, str], db: Session = Depends(get_db)) -> models.Tag:
    """Gets `Tag` object by `tag_key`.

    Args:
        `tag_key` (Union[int, str]): `Tag` object's id or title.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Tag`: `Tag` object.
    """

    if isinstance(tag_key, int):
        return crud.get_object(cls=models.Tag, db=db, object_id=tag_key)
    return crud.get_object_by_expression(cls=models.Tag, db=db, expression=(models.Tag.title == tag_key), raise_404=True)


@router.patch('/{tag_id}/', response_model=schemas.Tag)
@raise_403_if_not_admin
def update_tag(
        tag_id: int,
        tag: schemas.TagUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Tag:
    """Updates `Tag` object by `tag_id`.

    Args:
        `tag_id` (int): `Tag` object's id.
        `tag` (schemas.TagUpdate): `TagUpdate` schema.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Tag`: `Tag` object.
    """

    return crud.update_tag(db=db, tag_id=tag_id, tag=tag)


@router.delete('/{tag_id}/')
@raise_403_if_not_admin
def delete_tag(
        tag_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> Response:
    """Deletes a tag by a given `tag_id`.

    Args:
        `tag_id` (int): `Tag`'s id.
        `db` (Session, optional): Database connection.

    Returns:
        `Response`: No content response.
    """

    crud.delete_object(cls=models.Tag, db=db, object_id=tag_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
