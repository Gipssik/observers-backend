from fastapi import APIRouter

from . import articles

router = APIRouter(prefix='/news')

router.include_router(articles.router)
