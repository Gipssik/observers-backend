from typing import Union
from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm.session import Session

from database import crud, models, schemas
from dependencies import get_db, get_current_user

router = APIRouter(prefix='/questions', tags=['questions'])


@router.post('/', response_model=schemas.Question)
def create_question(
        question: schemas.QuestionCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Question:
    """Creates a `Question` object with a given `QuestionCreate` schema.

    Args:
        `question` (schemas.QuestionCreate): A `schemas.QuestionCreate` object.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Question`: `Question` object.
    """

    if question.author_id is None:
        question.author_id = current_user.id

    return crud.create_question(db=db, question=question)


@router.get('/', response_model=list[schemas.Question])
def get_questions(
        skip: int = 0,
        limit: int = 100,
        by_title: str = None,
        order_by_date: str = None,
        order_by_views: bool = None,
        db: Session = Depends(get_db)
) -> list[models.Question]:
    """Gets all `Questions` from database in range [`skip`:`skip+limit`] and returns them to the client.

    Args:
        `skip` (Optional[int], optional): How many objects to skip. Defaults to 0.
        `limit` (Optional[int], optional): Maximum amount of objects. Defaults to 100.
        `by_title` (Optional[str], optional): Title to get by. Defaults to None.
        `order_by_date` (Optional[str], optional): Method of sorting by date. Defaults to None.
        `order_by_views` (Optional[bool], optional): To sort by views or not. Defaults to None.
        `db` (Session, optional): Database connection.

    Returns:
        `list[models.Question]`: A `list` of all `Question` objects.
    """

    if by_title:
        return crud.get_questions_by_title(db=db, title=by_title)

    if order_by_date:
        if order_by_date.lower() == 'desc':
            return crud.get_objects(
                cls=models.Question,
                db=db,
                skip=skip,
                limit=limit,
                order_by=models.Question.date_created.desc()
            )
        elif order_by_date.lower() == 'asc':
            return crud.get_objects(
                cls=models.Question,
                db=db,
                skip=skip,
                limit=limit,
                order_by=models.Question.date_created.asc()
            )
    elif order_by_views:
        return crud.get_objects(
            cls=models.Question,
            db=db,
            skip=skip,
            limit=limit,
            order_by=models.Question.views.desc()
        )
    return crud.get_objects(cls=models.Question, db=db, skip=skip, limit=limit)


@router.get('/{question_title}/title/', response_model=list[schemas.Question])
def get_questions_by_title(question_title: str, db: Session = Depends(get_db)) -> list[models.Question]:
    return crud.get_questions_by_title(db=db, title=question_title)


@router.get('/{question_id}/', response_model=schemas.Question)
def get_question(question_id: int, db: Session = Depends(get_db)) -> models.Question:
    """Gets `Question` object by `question_key`.

    Args:
        `question_id` (int): `Question` object's id.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Question`: `Question` object.
    """

    return crud.get_object(cls=models.Question, db=db, object_id=question_id)


@router.get('/{user_id}/user/', response_model=list[schemas.Question])
def get_questions_by_user(user_id: int, db: Session = Depends(get_db)) -> list[models.Question]:
    """Returns a list of user's questions by `user_id`.

    Args:
        `user_id` (int): User's id.
        `db` (): Database connection.

    Returns:
        `list[models.Question]`: List of `Question` objects.
    """

    return crud.get_objects_by_expression(
        cls=models.Question,
        db=db,
        expression=(models.Question.author_id == user_id),
    )


@router.patch('/{question_id}/', response_model=schemas.Question)
def update_question(
        question_id: int,
        question: schemas.QuestionUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> models.Question:
    """Updates `Question` object by `question_id`.

    Args:
        `question_id` (int): `Question` object's id.
        `question` (schemas.QuestionUpdate): `QuestionUpdate` schema.
        `db` (Session, optional): Database connection.

    Returns:
        `models.Question`: `Question` object.
    """

    if current_user.role.title != 'Admin' and \
            current_user.id != crud.get_object(cls=models.Question, db=db, object_id=question_id).author.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You did not give the views parameter.'
        )

    return crud.update_question(db=db, question_id=question_id, question=question)


@router.patch('/{question_id}/views/')
def update_question_views(question_id: int, views: int, db: Session = Depends(get_db)) -> models.Question:
    """Updates question views by a given `question_id`.

    Args:
        `question_id` (int):
        `views` (int):
        `db` (Session, optional): Database connection.

    Returns:
        `models.Question`: `Question` object.
    """

    return crud.update_question(
        db=db, question_id=question_id, question=schemas.QuestionUpdate(views=views)
    )


@router.delete('/{question_id}/')
def delete_question(
        question_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
) -> Response:
    """Deletes a question by a given `question_id`.

    Args:
        `question_id` (int): `Question`'s id.
        `db` (Session, optional): Database connection.

    Raises:
        `HTTPException`: If an invalid `question_id` was given.

    Returns:
        `Response`: No content response.
    """

    if current_user.role.title != 'Admin' and\
            current_user.id != crud.get_object(cls=models.Question, db=db, object_id=question_id).author.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not the owner of the question.'
        )

    crud.delete_object(cls=models.Question, db=db, object_id=question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
