from datetime import timedelta
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import (
    DefaultRoleNotFoundError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
)
from app.auth.utils.tokens_passwords import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.models.role import Role, RoleModel
from app.models.user import UserModel
from app.schemas.auth import CreateUser, TokenInfo, UserLogin


class AuthService:
    def __init__(self, db_session: AsyncSession, redis_client: Redis) -> None:
        self.db: AsyncSession = db_session
        self.redis: Redis = redis_client

    async def _get_default_role(self) -> RoleModel:
        role_query = await self.db.execute(
            select(RoleModel).where(RoleModel.title == Role.USER)
        )
        default_role: RoleModel | None = role_query.scalar_one_or_none()

        if not default_role:
            raise DefaultRoleNotFoundError("Default user role not found in database")

        return default_role

    async def _create_user_session(self, user: UserModel) -> TokenInfo:
        token_payload: dict[str, Any] = {"sub": str(user.id), "email": user.email}
        access_token: str = create_access_token(data=token_payload)
        refresh_token: str = create_refresh_token(data=token_payload)

        redis_key: str = f"refresh_token:{user.id}"
        expire_seconds: int = int(
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()
        )

        await self.redis.set(
            name=redis_key,
            value=refresh_token,
            ex=expire_seconds,
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
