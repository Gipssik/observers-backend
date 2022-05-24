from fastapi import APIRouter

from . import questions, tags, comments

router = APIRouter(prefix='/forum')

router.include_router(questions.router)
router.include_router(tags.router)
router.include_router(comments.router)
