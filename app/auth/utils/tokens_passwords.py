from datetime import datetime, timedelta, timezone
from typing import Any

from bcrypt import checkpw, gensalt, hashpw
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode

from app.core.config import settings


def hash_password(password: str) -> str:
    salt: bytes = gensalt()
    pwd_bytes: bytes = password.encode("utf-8")
    return hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, Any] = data.copy()

    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt: str = encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode: dict[str, Any] = data.copy()
    expire: datetime = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})

    encoded_jwt: str = encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str, is_refresh: bool = False) -> dict[str, Any] | None:

    secret_key: str = (
        settings.JWT_REFRESH_SECRET_KEY if is_refresh else settings.JWT_SECRET_KEY
    )

    try:
        payload: dict[str, Any] = decode(
            token, secret_key, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None
