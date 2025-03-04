from typing import AsyncIterator

from redis.asyncio import Redis, from_url


async def init_redis_client(url: str) -> AsyncIterator[Redis]:
    session = from_url(url, encoding='UTF-8')

    yield session

    session.close()

    await session.wait_closed()
