import datetime
from enum import Enum
from typing import ForwardRef, List, Optional

from pydantic import BaseModel, EmailStr

User = ForwardRef('User')
Notification = ForwardRef('Notification')
Question = ForwardRef('Question')
Comment = ForwardRef('Comment')


class RoleBase(BaseModel):
    title: str

    class Config:
        orm_mode = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    title: Optional[str] = None


class Role(RoleBase):
    id: int
    users: list[User] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role_id: int


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None


class User(UserBase):
    id: int
    role: RoleBase
    date_created: datetime.datetime
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    title: str
    user_id: int
    question_id: int


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = None


class Notification(NotificationBase):
    id: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    title: str

    class Config:
        orm_mode = True


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    title: Optional[str] = None


class Tag(TagBase):
    id: int
    questions: list[Question] = []

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):
    title: str
    content: str


class QuestionCreate(QuestionBase):
    tags: Optional[list[str]] = None
    author_id: Optional[int] = None


class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    views: Optional[int] = None


class Question(QuestionBase):
    id: int
    author_id: int
    date_created: datetime.datetime
    views: int
    tags: list[TagBase] = []

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str
    question_id: int


class CommentCreate(CommentBase):
    author_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_answer: Optional[bool] = None


class Comment(CommentBase):
    id: int
    author_id: int
    date_created: datetime.datetime
    is_answer: bool

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    title: str
    content: str


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Article(ArticleBase):
    id: int
    date_created: datetime.datetime
    likes: list[User]
    dislikes: list[User]

    class Config:
        orm_mode = True


class ArticleRatingType(str, Enum):
    likes = 'likes'
    dislikes = 'dislikes'


Role.update_forward_refs()
User.update_forward_refs()
Tag.update_forward_refs()
Question.update_forward_refs()
