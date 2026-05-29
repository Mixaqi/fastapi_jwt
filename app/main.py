from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.core.db_helper import db_helper
from app.core.exceptions.handlers import auth_exception_handler
from app.services.exceptions import AuthError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await db_helper.engine.dispose()


app = FastAPI(title="Geoapp_FastAPI", lifespan=lifespan)

app.add_exception_handler(AuthError, auth_exception_handler)  # type: ignore[arg-type]

app.include_router(auth_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
