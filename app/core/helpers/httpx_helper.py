from collections.abc import AsyncGenerator

from httpx import AsyncClient


class HTTPClientHelper:
    def __init__(self) -> None:
        self.client: AsyncClient | None = None

    def init_client(self) -> None:
        self.client = AsyncClient()

    async def close_client(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None

    def get_client(self) -> AsyncClient:
        if self.client is None:
            raise RuntimeError("HTTPClientHelper is not initialized")
        return self.client


httpx_helper = HTTPClientHelper()


async def get_http_client() -> AsyncGenerator[AsyncClient]:
    yield httpx_helper.get_client()
