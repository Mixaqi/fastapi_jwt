from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.db_helper import get_async_psql_session
from app.core.redis_helper import get_redis_client
from app.models.user import UserModel
from app.schemas.auth import CreateUser, TokenInfo, UserLogin, UserRefresh, UserSchema
from app.services.auth import AuthService
from app.services.exceptions import (
    DefaultRoleNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
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


@router.post(
    "/refresh",
    response_model=TokenInfo,
    status_code=status.HTTP_200_OK,
    summary="Refresh access and refresh tokens",
)
async def refresh(
    refresh_data: UserRefresh,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenInfo:
    try:
        return await auth_service.refresh_tokens(
            refresh_token=refresh_data.refresh_token
        )
    except InvalidTokenError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except UserInactiveError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user and revoke refresh token",
)
async def logout(
    refresh_data: UserRefresh,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.logout(refresh_token=refresh_data.refresh_token)


@router.get("/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_me(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    return current_user
