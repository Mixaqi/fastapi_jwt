from datetime import timedelta
from typing import Any

from jwt import DecodeError, decode
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.role import Role, RoleModel
from app.models.user import UserModel
from app.schemas.auth import CreateUser, TokenInfo, UserLogin
from app.services.exceptions import (
    DefaultRoleNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserInactiveError,
)


class AuthService:
    def __init__(self, db_session: AsyncSession, redis_client: Redis) -> None:
        self.db: AsyncSession = db_session
        self.redis: Redis = redis_client

    def _get_redis_key(self, user_id: int | str) -> str:
        return f"refresh_token:{user_id}"

    async def _get_default_role(self) -> RoleModel:
        role_query = await self.db.execute(
            select(RoleModel).where(RoleModel.title == Role.USER)
        )
        default_role: RoleModel | None = role_query.scalar_one_or_none()

        if not default_role:
            raise DefaultRoleNotFoundError("Default user role not found in database")

        return default_role

    async def _create_user_session(self, user: UserModel) -> TokenInfo:
        access_payload: dict[str, Any] = {"sub": str(user.id), "email": user.email}
        refresh_payload: dict[str, Any] = {"sub": str(user.id)}

        access_token: str = create_access_token(data=access_payload)
        refresh_token: str = create_refresh_token(data=refresh_payload)

        redis_key: str = self._get_redis_key(user.id)
        await self.redis.set(
            name=redis_key,
            value=refresh_token,
            ex=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        )
        return TokenInfo(access_token=access_token, refresh_token=refresh_token)

    async def register_user(self, user_data: CreateUser) -> UserModel:
        default_role = await self._get_default_role()

        new_user: UserModel = UserModel(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            is_active=True,
        )
        new_user.roles.append(default_role)

        self.db.add(new_user)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise UserAlreadyExistsError(
                "User with this email or username already exists"
            )
        await self.db.refresh(new_user)
        return new_user

    async def authenticate_user(self, login_data: UserLogin) -> TokenInfo:
        user_query = await self.db.execute(
            select(UserModel).where(UserModel.email == login_data.email)
        )
        user: UserModel | None = user_query.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password")

        if not user.is_active:
            raise UserInactiveError("User account is deactivated")

        return await self._create_user_session(user)

    async def refresh_tokens(self, refresh_token: str) -> TokenInfo:
        payload: dict[str, Any] | None = decode_token(refresh_token, is_refresh=True)

        if payload is None:
            raise InvalidTokenError("Invalid or expired refresh token")

        user_id: int | None = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Invalid token payload")

        redis_key: str = self._get_redis_key(user_id)
        saved_refresh_token: str = await self.redis.get(redis_key)

        if not saved_refresh_token or str(saved_refresh_token) != refresh_token:
            raise InvalidTokenError("Refresh token has been revoked or expired")

        user_query = await self.db.execute(
            select(UserModel).where(UserModel.id == int(user_id))
        )
        user: UserModel | None = user_query.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError("User not found")

        if not user.is_active:
            raise UserInactiveError("User account is deactivated")

        return await self._create_user_session(user)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload: dict[str, Any] = decode(
                refresh_token,
                settings.JWT_REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False},
            )

            user_id: str | None = payload.get("sub")

            if user_id:
                redis_key: str = self._get_redis_key(user_id)
                await self.redis.delete(redis_key)

        except DecodeError:
            raise InvalidTokenError("Invalid token format")

        except Exception:
            pass
