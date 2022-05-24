from fastapi import APIRouter

from . import notifications, roles, users

router = APIRouter(prefix='/accounts')

router.include_router(roles.router)
router.include_router(users.router)
router.include_router(notifications.router)
