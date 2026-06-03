import logging
from typing import Any

from fastapi import BackgroundTasks
from httpx import AsyncClient, HTTPError, HTTPStatusError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user_page_history import UserPageHistoryModel
from app.services.page.exceptions import DjangoIntegrationError


logger = logging.getLogger(__name__)


class PageService:
    def __init__(self, client: AsyncClient, session: AsyncSession) -> None:
        self.client = client
        self.session = session

    async def _log_user_pages_view(self, user_id: int, page_ids: list[int]) -> None:
        if not page_ids:
            return

        try:
            history_entries = [
                UserPageHistoryModel(user_id=user_id, page_id=page_id)
                for page_id in page_ids
            ]
            self.session.add_all(history_entries)
            await self.session.commit()

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("SQLAlchemy Error: %s", e)

    async def get_pages_list_and_track_history(
        self, user_id: int, background_tasks: BackgroundTasks
    ) -> dict[str, Any]:

        url = settings.django.api_url

        headers = {
            "X-Internal-Secret": settings.django.internal_secret_key,
            "X-User-Id": str(user_id),
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.get(url, headers=headers, timeout=5.0)
            response.raise_for_status()
            django_data: dict[str, Any] = response.json()

        except HTTPStatusError as e:
            raise DjangoIntegrationError(
                f"Django error {e.response.status_code}: {e.response.text}"
            )
        except HTTPError as e:
            raise DjangoIntegrationError(
                f"Cannot connect with Django service: {str(e)}"
            )

        results: list[dict[str, Any]] = django_data.get("results", [])

        page_ids: list[int] = [
            item["id"] for item in results if isinstance(item, dict) and "id" in item
        ]

        if page_ids:
            background_tasks.add_task(self._log_user_pages_view, user_id, page_ids)

        return django_data
