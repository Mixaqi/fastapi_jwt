from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import get_async_psql_session
from app.core.redis_helper import get_redis_client
from app.models.user import UserModel
from app.schemas.auth import CreateUser, TokenInfo, UserLogin, UserSchema
from app.services.auth import AuthService
from app.services.exceptions import (
    DefaultRoleNotFoundError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
)


router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(
    db_session: AsyncSession = Depends(get_async_psql_session),
    redis_client: Redis = Depends(get_redis_client),
) -> AuthService:
    return AuthService(db_session=db_session, redis_client=redis_client)


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
)
async def register(
    user_data: CreateUser,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserModel:
    try:
        return await auth_service.register_user(user_data=user_data)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except DefaultRoleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.post(
    "/login",
    response_model=TokenInfo,
    status_code=status.HTTP_200_OK,
    summary="Login user",
)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenInfo:
    try:
        return await auth_service.authenticate_user(login_data=login_data)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except UserInactiveError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
