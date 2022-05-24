from fastapi import APIRouter

from . import users, forum, news, chat

router = APIRouter(prefix='/api')

router.include_router(users.router)
router.include_router(forum.router)
router.include_router(news.router)
router.include_router(chat.router)
