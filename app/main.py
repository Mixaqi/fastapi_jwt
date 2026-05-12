from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await db_helper.engine.dispose()


app = FastAPI(
    title="Geoapp_FastAPI", lifespan=lifespan
)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)