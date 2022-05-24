from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the given `password` is correct.

    Args:
        `plain_password` (str): A given `password`.
        `hashed_password` (str): A hashed `password` form database.

    Returns:
        `bool`: True if the `password` is correct, otherwise `False`.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Returns a hashed `password`.

    Args:
        `password` (str): A plain `password` as a string.

    Returns:
        `str`: A hashed `password` as a string.
    """

    return pwd_context.hash(password)
