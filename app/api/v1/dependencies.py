from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.core.security import decode_token


security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token: str = credentials.credentials

    payload: dict[str, Any] | None = decode_token(token)

    if payload is None:
        raise InvalidTokenError("Invalid access token")

    user_id: str | None = payload.get("sub")

    if not user_id:
        raise InvalidTokenError("Invalid token payload")

    return int(user_id)
