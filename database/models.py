import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from .db import Base

tag_question = Table(
    'tag_question', Base.metadata,
    Column('tag_id', ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True, index=True),
    Column('question_id', ForeignKey('questions.id', ondelete='CASCADE'), primary_key=True, index=True)
)

users_like_article = Table(
    'users_like_article', Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True),
    Column('article_id', ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True, index=True)
)

users_dislike_article = Table(
    'users_dislike_article', Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True),
    Column('article_id', ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True, index=True)
)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)

    users = relationship('User', backref='role', cascade='all,delete')

    def __repr__(self) -> str:
        return f'Role("{self.title}")'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    profile_image = Column(String, nullable=False, default='default.jpg')
    role_id = Column(Integer, ForeignKey('roles.id'))

    notifications = relationship('Notification', backref='user', cascade='all,delete')
    questions = relationship('Question', backref='author', cascade='all,delete')
    comments = relationship('Comment', backref='author', cascade='all,delete')

    def __repr__(self) -> str:
        return f'User("{self.username}")'


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))

    def __repr__(self) -> str:
        return f'Notification("{self.user.username}", "{self.question.title}")'


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)

    questions = relationship('Question', secondary=tag_question, backref='tags')

    def __repr__(self) -> str:
        return f'Tag("{self.title}")'


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    views = Column(Integer, nullable=False, default=0)
    author_id = Column(Integer, ForeignKey('users.id'))

    notifications = relationship('Notification', backref='question', cascade='all,delete')
    comments = relationship('Comment', backref='question', cascade='all,delete')

    def __repr__(self) -> str:
        return f'Question("{self.title}", "{self.author.username}")'


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    is_answer = Column(Boolean, nullable=False, default=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))

    def __repr__(self) -> str:
        return f'Comment("{self.author.username}", "{self.content[:10]}...")'


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    likes = relationship('User', secondary=users_like_article, backref='likes')
    dislikes = relationship('User', secondary=users_dislike_article, backref='dislikes')

    def __repr__(self) -> str:
        return f'Article("{self.title}")'
