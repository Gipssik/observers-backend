from typing import Any

from fastapi import HTTPException, status
from fuzzywuzzy import fuzz
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .db import Base

from . import models, schemas
from security import hashing


def get_object(cls: type, db: Session, object_id: int) -> Base:
    """Returns a `cls` object by `object_id`.

    Args:
        `cls` (type): Type of the object to get.
        `db` (Session): Database connection.
        `object_id` (int): Object's id.

    Raises:
        `HTTPException`: If object with this id does not exist.

    Returns:
        `Base`: `Base` model object.
    """

    db_object = db.query(cls).get(object_id)

    if not db_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{cls.__name__.capitalize()} with this id does not exist.'
        )

    return db_object


def get_object_by_expression(cls: type, db: Session, expression: Any, raise_404: bool = False) -> Base:
    """Returns `cls` model object filtered by `expression`.

    Args:
        `cls` (type): Type of the object to get.
        `db` (Session): Database connection.
        `expression` (Any): Expression to filter function.
        `raise_404` (bool): To raise error 404 or not. Defaults to False.

    Returns:
        `Base`: `Base` model object.

    """
    obj = db.query(cls).filter(expression).first()

    if raise_404 and not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{cls.__name__.capitalize()} with this field does not exist.'
        )

    return obj


def get_objects_by_expression(cls: type, db: Session, expression: Any) -> list[Base]:
    """Returns list of `cls` model objects filtered by `expression`.

    Args:
        `cls` (type): Type of the object to get.
        `db` (Session): Database connection.
        `expression` (Any): Expression to filter function.

    Returns:
        `list[Base]`: List of `Base` model objects.

    """

    return db.query(cls).filter(expression).all()


def get_objects(cls: type, db: Session, skip: int = 0, limit: int = 100, order_by: any = None) -> list[Base]:
    """Returns all `Base` objects in range[`skip`:`skip+limit`].

    Args:
        `cls` (type): Type of the objects to get.
        `db` (Session): Database connection.
        `skip` (int, optional): Integer number of how many users you need to skip. Defaults to 0.
        `limit` (int, optional): Integer maximum number of how many users you need to get. Defaults to 100.

    Returns:
        `list[Base]`: All `Base` model objects.
    """

    if order_by is not None:
        return db.query(cls).order_by(order_by).offset(skip).limit(limit).all()
    return db.query(cls).offset(skip).limit(limit).all()


def delete_object(cls: type, db: Session, object_id: int) -> None:
    """Deletes object by a given `object_id`.

    Args:
        `cls` (type): Type of the object to delete.
        `db` (Session): Database connection.
        `object_id` (int): Object's id.

    Returns:
        `None`
    """

    db_object = get_object(cls=cls, db=db, object_id=object_id)

    db.delete(db_object)
    db.commit()
    return None


def update_object(cls: type, db: Session, object_id: int, schema_object: BaseModel) -> Base:
    """Updates `cls` object by given `object_id` and `schema_object`.

    Args:
        `cls` (type): Type of object model
        `db` (Session): Database connection.
        `object_id` (int): Object's id.
        `schema_object` (BaseModel): Pydantic object schema.

    Returns:
        `Base`: Updated `cls` object.
    """

    db_object = get_object(cls=cls, db=db, object_id=object_id)
    object_schema = schema_object.__class__(**db_object.__dict__)

    update_obj = schema_object.dict(exclude_unset=True)
    updated_obj = object_schema.copy(update=update_obj)

    db.query(cls).filter_by(id=object_id).update(updated_obj.__dict__)
    db.commit()
    db.refresh(db_object)

    return db_object


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    """Creates a model Role with a given `role` schema.

    Args:
        `db` (Session): Database connection.
        `role` (schemas.RoleCreate): Role Pydantic model.

    Raises:
        `HTTPException`: If there's no role with this `title`.

    Returns:
        `models.Role`: A new `Role`.
    """

    if get_object_by_expression(cls=models.Role, db=db, expression=(models.Role.title == role.title)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role with this title already exists."
        )

    db_role = models.Role(title=role.title)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role: schemas.RoleUpdate) -> models.Role:
    """Updates `Role` object by a given `role_id` using `role` schema.

    Args:
        `db` (Session): Database connection.
        `role_id` (int): `Role` object's id.
        `role` (schemas.RoleUpdate): Pydantic object's schema.

    Raises:
        `HTTPException`: If there's a role with the same title.

    Returns:
        `models.Role`: Updated `Role` object.
    """

    if (r := get_object_by_expression(cls=models.Role, db=db, expression=(models.Role.title == role.title)))\
        and r.id != role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Role with this title already exists.'
        )

    return update_object(cls=models.Role, db=db, object_id=role_id, schema_object=role)


def update_role_by_title(db: Session, role_title: str, role: schemas.RoleUpdate) -> models.Role:
    """Updates `Role` object by a given `role_title` using `role` schema.

    Args:
        `db` (Session): Database connection.
        `role_title` (int): `Role` object's title.
        `role` (schemas.RoleUpdate): Pydantic object's schema.

    Returns:
        `models.Role`: Updated `Role` object.
    """

    role_db = \
        get_object_by_expression(cls=models.Role, db=db, expression=(models.Role.title == role_title), raise_404=True)
    return update_role(db=db, role_id=role_db.id, role=role)


def delete_role_by_title(db: Session, title: str) -> None:
    """Deletes a `Role` object by a given `title`

    Args:
        `db` (Session): Database connection.
        `title` (str): The `title` of role.

    Returns:
        `None`
    """

    role = get_object_by_expression(cls=models.Role, db=db, expression=(models.Role.title == title), raise_404=True)

    db.delete(role)
    db.commit()

    return None


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Creates a User with a given `user` schema.

    Args:
        `db` (Session): Database connection.
        `user` (schemas.UserCreate): User Pydantic model.

    Raises:
        `HTTPException`: If there's a `user` with the same username or email.
        `HTTPException`: If there's no `role` with this `role_id`.

    Returns:
        `models.User`: A new `User`.
    """

    if db.query(models.User).filter(
        or_(models.User.username == user.username, models.User.email == user.email)).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this username or email already exists."
        )

    get_object(cls=models.Role, db=db, object_id=user.role_id)

    hashed_password = hashing.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    """Updates `User` object by a given `user_id` using `user` schema.

    Args:
        `db` (Session): Database connection.
        `user_id` (int): `User` object's id.
        `user` (schemas.UserUpdate): Pydantic object's schema.

    Raises:
        `HTTPException`: If there's a user with the same email.

    Returns:
        `models.User`: Updated `User` object.
    """

    db_user = get_object(cls=models.User, db=db, object_id=user_id)
    user_schema = schemas.UserUpdate(**db_user.__dict__)

    if user.email\
        and (u := get_object_by_expression(cls=models.User, db=db, expression=(models.User.email == user.email)))\
        and u.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User with this email already exists.'
        )

    if user.password:
        user.password = hashing.get_password_hash(user.password)

    update_data = user.dict(exclude_unset=True)
    updated_user = user_schema.copy(update=update_data)

    db.query(models.User).filter_by(id=user_id).update(updated_user.__dict__)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_notification(db: Session, notification: schemas.NotificationCreate) -> models.Notification:
    """Creates a `Notification` with a given schema.

    Args:
        `db` (Session): Database connection.
        `notification` (schemas.NotificationCreate): `schemas.NotificationCreate` object.

    Raises:
        HTTPException: If user with `user_id` does not exist.
        HTTPException: If question with `question_id` does not exist.

    Returns:
        models.Notification: A new `Notification` objects.
    """

    get_object(cls=models.User, db=db, object_id=notification.user_id)
    get_object(cls=models.Question, db=db, object_id=notification.question_id)

    notification_db = models.Notification(
        title=notification.title,
        user_id=notification.user_id,
        question_id=notification.question_id
    )

    db.add(notification_db)
    db.commit()
    db.refresh(notification_db)
    return notification_db


def get_notifications_by_user_id(db: Session, user_id: int, skip: int, limit: int) -> list[models.Notification]:
    """Returns notifications by a given `user_id`.

    Args:
        `db` (Session): Database connection.
        `user_id` (int): `User` object id.
        `skip` (int): How many objects to skip.
        `limit` (int): Maximum amout of objects.

    Raises:
        `HTTPException`: If there's no user with this `user_id`.

    Returns:
        `list[models.Notification]`: A list of `Notification` objects.
    """

    if not get_object(models.User, db=db, object_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id does not exist."
        )

    return db.query(models.Notification).order_by(models.Notification.id.desc())\
        .filter_by(user_id=user_id).offset(skip).limit(limit).all()


def delete_notifications_by_user_id(db: Session, user_id: int) -> None:
    """Deletes a `Notification` model objects with a given `user_id`

    Args:
        `db` (Session): Database connection.
        `user_id` (int): `User` object's id.

    Raises:
        `HTTPException`: If a user with this id does not exist.

    Returns:
        `None`
    """

    if not get_object(models.User, db=db, object_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id does not exist."
        )

    db.query(models.Notification).filter_by(user_id=user_id).delete()
    db.commit()

    return None


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    """Creates a `Tag` model object with a given `tag` schema

    Args:
        `db` (Session): Database connection.
        `tag` (schemas.TagCreate): `Tag` schema.

    Raises:
        `HTTPException`: If a tag with this title already exists.

    Returns:
        `models.Tag`: `Tag` object.
    """

    if get_object_by_expression(cls=models.Tag, db=db, expression=(models.Tag.title == tag.title)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Tag with this title already exist.'
        )

    tag_db = models.Tag(title=tag.title)
    db.add(tag_db)
    db.commit()
    return tag_db


def update_tag(db: Session, tag_id: int, tag: schemas.TagUpdate) -> models.Tag:
    """Updates `Tag` object by a given `tag_id` using `tag` schema.

    Args:
        `db` (Session): Database connection.
        `tag_id` (int): `Tag` object's id.
        `tag` (schemas.TagUpdate): Pydantic object's schema.

    Raises:
        `HTTPException`: If there's a tag with the same title.

    Returns:
        `models.Tag`: Updated `Tag` object.
    """

    if (t := get_object_by_expression(cls=models.Tag, db=db, expression=(models.Tag.title == tag.title))) and \
            t.id != tag_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Tag with this title already exists.'
        )

    return update_object(cls=models.Tag, db=db, object_id=tag_id, schema_object=tag)


def fill_tags(db: Session, tags: list[str], question_db: models.Question) -> None:
    """Adds `tags` to a given `question_db`.

    Args:
        `db` (Session): Database connection.
        `tags` (list[str]): List of tags.
        `question_db` (models.Question): `Question` object.

    Raises:
        `HTTPException`: If there was a wrong tag given.
    """

    if not tags:
        return

    for tag in tags:
        tag = tag.lower()
        if not tag.replace('.', '').replace('-', '').replace('_', '').isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Wrong tag title.'
            )

        if not (tag_db := get_object_by_expression(cls=models.Tag, db=db, expression=(models.Tag.title == tag))):
            tag_db = models.Tag(title=tag)
            db.add(tag_db)

        question_db.tags.append(tag_db)


def create_question(db: Session, question: schemas.QuestionCreate) -> models.Question:
    """Creates a `Question` object if `User` with a given `user_id` exists.

    Args:
        `db` (Session): Database connection.
        `question` (schemas.QuestionCreate): A `schemas.QuestionCreate` schema.

    Raises:
        `HTTPException`: If `User` with `user_id` does not exist.

    Returns:
        `models.Question`: A `Question` object.
    """

    get_object(cls=models.User, db=db, object_id=question.author_id)

    question_db = models.Question(
        title=question.title,
        content=question.content,
        author_id=question.author_id
    )

    db.add(question_db)

    fill_tags(db=db, tags=question.tags, question_db=question_db)

    db.commit()
    db.refresh(question_db)
    return question_db


def get_questions_by_title(db: Session, title: str) -> list[models.Question]:
    """Seeks for fuzzy equal question title to `title`.

    Args:
        `db` (Session): Database connection.
        `title` (str): `Question` object's title.

    Raises:
        `HTTPException`: If there's no fuzzy equal question title.

    Returns:
        `models.Question`: `Question` object.
    """

    questions = sorted(
        [(question, c) for question in db.query(models.Question).all()
        if (c := fuzz.WRatio(question.title, title)) >= 60],
        key=lambda x: x[1], reverse=True
    )

    return [question[0] for question in questions]


def update_question(db: Session, question_id: int, question: schemas.QuestionUpdate) -> models.Question:
    """Updates `Question` object by given `question_id` and `question` schema.

    Args:
        `db` (Session): Database connection.
        `question_id` (int): Question's id.
        `question` (schemas.QuestionUpdate): Pydantic question schema.

    Returns:
        `Base`: Updated `Question` object.
    """

    question_db = get_object(cls=models.Question, db=db, object_id=question_id)
    question_schema = schemas.QuestionUpdate(**question_db.__dict__)

    upd_question = question.dict(exclude_unset=True, exclude={'tags'})
    updated_question = question_schema.copy(update=upd_question, exclude={'tags'})

    db.query(models.Question).filter_by(id=question_id).update(updated_question.__dict__)

    if question.tags:
        question_db.tags = []
        fill_tags(db=db, tags=question.tags, question_db=question_db)

    db.commit()
    db.refresh(question_db)

    return question_db


def create_comment(db: Session, comment: schemas.CommentCreate) -> models.Comment:
    """Creates a `Comment` model object with a given `comment` schema

    Args:
        `db` (Session): Database connection.
        `comment` (schemas.CommentCreate): `Comment` schema.

    Raises:
        `HTTPException`: If a given user or question with this id does not exist.

    Returns:
        `models.Comment`: `Comment` object.
    """

    if not get_object(cls=models.User, db=db, object_id=comment.author_id)\
            or not get_object(cls=models.Question, db=db, object_id=comment.question_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User or question with this id does not exist.'
        )

    comment_db = models.Comment(
        content=comment.content,
        author_id=comment.author_id,
        question_id=comment.question_id
    )

    db.add(comment_db)
    db.commit()

    if comment.author_id != comment_db.question.author.id:
        create_notification(
            db=db,
            notification=schemas.NotificationCreate(
                title=f'User {comment_db.author.username} commented your question: "{comment_db.question.title}".',
                user_id=comment_db.question.author.id,
                question_id=comment_db.question_id
            )
        )

    return comment_db


def get_comments_by_question_id(db: Session, question_id: int) -> list[models.Comment]:
    """Returns all comments with `question_id`.

    Args:
        `db` (Session): Database connection.
        `question_id` (int): `Question` object's id..

    Returns:
        `list[models.Comment]`: List of `Comment` objects.
    """

    comments = db.query(models.Comment)\
        .order_by(models.Comment.date_created.asc())\
        .filter_by(question_id=question_id).all()
    return comments


def create_article(db: Session, article: schemas.ArticleCreate) -> models.Article:
    """Creates a model Article with a given `article` schema.

    Args:
        `db` (Session): Database connection.
        `article` (schemas.ArticleCreate): Article Pydantic model.

    Returns:
        `models.Article`: A new `Article`.
    """

    article_db = models.Article(title=article.title, content=article.content)

    db.add(article_db)
    db.commit()

    return article_db


def update_article_rating(db: Session, article_id: int, user: schemas.User, rating_type: str) -> models.Article:
    """Updates article's rating by a given `article_id` and `rating_type`.

    Args:
        `db` (Session): Database connection.
        `article_id` (int): `Article` object's id.
        `user` (schemas.User): Current `User` object.
        `rating_type` (str): Enum string - 'likes' or 'dislikes'

    Returns:
        `models.Article`: `Article` object.
    """

    article_db = get_object(cls=models.Article, db=db, object_id=article_id)
    user_db = get_object(cls=models.User, db=db, object_id=user.id)

    data_main = getattr(article_db, rating_type)

    if user_db in data_main:
        data_main.pop(data_main.index(user_db))
        setattr(article_db, rating_type, data_main)
    elif user_db not in data_main:
        data_main.append(user_db)
        setattr(article_db, rating_type, data_main)
        names = schemas.ArticleRatingType._member_names_
        data_secondary = getattr(article_db, names[names.index(rating_type) - 1])
        if user_db in data_secondary:
            data_secondary.pop(data_secondary.index(user_db))
            setattr(article_db, names[names.index(rating_type) - 1], data_secondary)

    db.commit()
    db.refresh(article_db)
    return article_db
