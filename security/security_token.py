import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(64)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates access token with a given `data` and `expires_delta`.

    Args:
        `data` (dict): A `dict` where exists a key "sub" with value of username.
        `expires_delta` (Optional[timedelta], optional): Time of token expiration. Defaults to None.

    Returns:
        `str`: A Json Web Token.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
