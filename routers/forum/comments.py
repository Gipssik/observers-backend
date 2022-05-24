from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm.session import Session

from database import crud, models, schemas
from decorators import raise_403_if_not_admin
from dependencies import get_db, get_current_user

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post('/', response_model=schemas.Comment)
def create_comment(
        comment: schemas.CommentCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Comment:
    """Creates a `Comment` object with a given `CommentCreate` schema.

    Args:
        `comment` (schemas.QuestionCreate): A `schemas.CommentCreate` object.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Comment`: `Comment` object.
    """

    comment.author_id = current_user.id
    return crud.create_comment(db=db, comment=comment)


@router.get('/', response_model=list[schemas.Comment])
@raise_403_if_not_admin
def get_comments(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> list[models.Comment]:
    """Gets all `Comments` from database in range [`skip`:`skip+limit`] and returns them to the client.

    Args:
        `skip` (Optional[int], optional): How many objects to skip. Defaults to 0.
        `limit` (Optional[int], optional): Maximum amount of objects. Defaults to 100.
        `db` (Session, optional): Database connection.

    Returns:
        `list[models.Comment]`: A `list` of all `Comment` objects.
    """

    return crud.get_objects(cls=models.Comment, db=db, skip=skip, limit=limit)


@router.get('/{question_id}/', response_model=list[schemas.Comment])
def get_comments_by_question(question_id: int, db: Session = Depends(get_db)) -> list[models.Comment]:
    """Gets all `Comments` with `question_id` from database and returns them to the client.

    Args:
        `question_id` (int): `Question` object's id.
        `db` (Session, optional): Database connection.

    Returns:
        `list[models.Comment]`: List of `Comment` objects.
    """

    return crud.get_comments_by_question_id(db=db, question_id=question_id)


@router.patch('/{comment_id}/', response_model=schemas.Comment)
def update_comment(
        comment_id: int,
        comment: schemas.CommentUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Comment:
    """Updates `Comment` object by `comment_id`.

    Args:
        `comment_id` (int): `Comment` object's id.
        `comment` (schemas.CommentUpdate): `CommentUpdate` schema.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Comment`: `Comment` object.
    """

    if current_user.role.title == 'Admin':
        return crud.update_object(cls=models.Comment, db=db, object_id=comment_id, schema_object=comment)

    comment_db = crud.get_object(cls=models.Comment, db=db, object_id=comment_id)

    if comment.content and current_user.id == comment_db.author.id:
        return crud.update_object(
            cls=models.Comment,
            db=db,
            object_id=comment_id,
            schema_object=schemas.CommentUpdate(content=comment.content)
        )

    elif comment.is_answer is not None and current_user.id == comment_db.question.author.id:
        return crud.update_object(
            cls=models.Comment,
            db=db,
            object_id=comment_id,
            schema_object=schemas.CommentUpdate(is_answer=comment.is_answer)
        )


@router.delete('/{comment_id}/')
def delete_question(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> Response:
    """Deletes a comment by a given `comment_id`.

    Args:
        `comment_id` (int): `Comment`'s id.
        `db` (Session, optional): Database connection.

    Raises:
        `HTTPException`: If an invalid `comment_id` was given.

    Returns:
        `Response`: No content response.
    """

    if current_user.role.title == 'Admin' or\
            current_user.id == crud.get_object(cls=models.Comment, db=db, object_id=comment_id).author.id:
        crud.delete_object(cls=models.Comment, db=db, object_id=comment_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not author of comment.'
        )
