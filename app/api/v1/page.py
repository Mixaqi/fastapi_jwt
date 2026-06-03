from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.helpers import db_helper
from app.core.helpers.httpx_helper import get_http_client
from app.models.user import UserModel
from app.services.page.exceptions import DjangoIntegrationError
from app.services.page.page import PageService


router = APIRouter(prefix="/pages", tags=["Pages"])


@router.get("/")
async def get_pages(
    background_tasks: BackgroundTasks,
    client: AsyncClient = Depends(get_http_client),
    session: AsyncSession = Depends(db_helper.get_async_psql_session),
    current_user: UserModel = Depends(get_current_user),
) -> dict[str, Any]:

    page_service = PageService(client=client, session=session)

    try:
        return await page_service.get_pages_list_and_track_history(
            user_id=current_user.id,
            background_tasks=background_tasks,
        )
    except DjangoIntegrationError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
