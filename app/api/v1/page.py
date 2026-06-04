from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
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
    request: Request,
    background_tasks: BackgroundTasks,
    client: AsyncClient = Depends(get_http_client),
    session: AsyncSession = Depends(db_helper.get_async_psql_session),
    current_user: UserModel = Depends(get_current_user),
    owner: int | None = Query(default=None, description="Owner username filter"),
    contact_person_name: int | None = Query(
        default=None, description="Contact person name filter"
    ),
    contact_person_email: str | None = Query(
        default=None, description="Contact person email filter"
    ),
    contact_person_phone: str | None = Query(
        default=None, description="Contact person phone filter"
    ),
    search: str | None = Query(default=None, description="Title page filter"),
    ordering: str | None = Query(
        default=None, description="Sorting. (id, -id, title, -title)"
    ),
    page: int | None = Query(default=None, description="Page number"),
    limit: int | None = Query(default=None, description="Number of items to show"),
    offset: int | None = Query(
        default=None, description="how many elements u need to skip"
    ),
) -> dict[str, Any]:

    page_service = PageService(client=client, session=session)
    query_params = request.query_params.multi_items()
    try:
        return await page_service.get_pages_list_and_track_history(
            user_id=current_user.id,
            background_tasks=background_tasks,
            query_params=query_params,
        )
    except DjangoIntegrationError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
