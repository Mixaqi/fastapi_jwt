from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.security import decode_token
from app.models.user import UserModel
from app.services.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserInactiveError,
)


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(db_helper.get_async_psql_session),
) -> UserModel:
    token: str = credentials.credentials

    payload: dict[str, Any] | None = decode_token(token)

    if payload is None:
        raise InvalidTokenError("Invalid access token")

    user_id: str | None = payload.get("sub")

    if not user_id:
        raise InvalidTokenError("Invalid token payload")

    query = select(UserModel).where(UserModel.id == int(user_id))
    result = await session.execute(query)
    user: UserModel | None = result.scalar_one_or_none()

    if not user:
        raise InvalidCredentialsError("User not found")

    if not user.is_active:
        raise UserInactiveError("User account is deactivated")

    return user
