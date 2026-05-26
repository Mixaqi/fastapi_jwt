from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    client: Redis = Redis.from_url(
        settings.redis.get_redis_URL,
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.close()
