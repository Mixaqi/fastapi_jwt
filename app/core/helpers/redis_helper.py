from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings


class RedisHelper:
    def __init__(self, url: str) -> None:
        self.url = url
        self.client: Redis | None = None

    def init_client(self) -> None:
        self.client = Redis.from_url(
            self.url,
            decode_responses=True,
        )

    async def close_client(self) -> None:
        if self.client:
            await self.client.close()
            self.client = None

    def get_client(self) -> Redis:
        if self.client is None:
            raise RuntimeError("RedisHelper is not initialized")
        return self.client


redis_helper = RedisHelper(url=settings.redis.get_redis_URL)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    yield redis_helper.get_client()
