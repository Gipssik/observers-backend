from functools import wraps

from fastapi import HTTPException, status


def raise_403_if_not_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if (user := kwargs.get('current_user')) and user.role.title != 'Admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You are not an admin.'
            )
        return func(*args, **kwargs)

    return wrapper


def raise_403_if_no_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if (user := kwargs.get('current_user')) \
                and user.role.title != 'Admin' \
                and user.id != kwargs.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You are not that user.'
            )
        return func(*args, **kwargs)

    return wrapper
