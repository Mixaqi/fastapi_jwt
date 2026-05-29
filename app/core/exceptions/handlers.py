from fastapi import Request
from fastapi.responses import JSONResponse

from app.services.exceptions import AuthError


async def auth_exception_handler(request: Request, exc: AuthError) -> JSONResponse:

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "code": exc.error_code,
        },
    )
