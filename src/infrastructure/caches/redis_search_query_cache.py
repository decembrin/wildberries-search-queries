import hashlib
import pickle
from typing import Optional

from redis.asyncio import Redis

from application.interfaces.search_query_cache_interface import (
    ISearchQueryCache,
)
from domain.entities.search_query_entity import SearchQueryEntity


class RedisSearchQueryCache(ISearchQueryCache):
    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    async def get_query_by_id(self, query_id: int) -> Optional[SearchQueryEntity]:
        key = 'wsq:query_by_id:{id}'.format(
            id=hashlib.md5(str(query_id).encode('UTF-8')).hexdigest(),
        )
        raw_value = await self._redis.get(key)

        return self._bytes_to_entity(raw_value)

    async def get_query_by_value(self, query_value: int) -> Optional[SearchQueryEntity]:
        key = 'wsq:query_by_value:{value}'.format(
            value=hashlib.md5(query_value.encode('UTF-8')).hexdigest(),
        )
        raw_value = await self._redis.get(key)

        return self._bytes_to_entity(raw_value)

    async def save_search_query(self, query: SearchQueryEntity, ttl: int = None) -> None:
        if query is None:
            return

        raw_value = self._entity_to_bytes(query)

        key = 'wsq:query_by_value:{value}'.format(
            value=hashlib.md5(query.value.encode('UTF-8')).hexdigest(),
        )
        await self._redis.set(key, raw_value, ex=ttl)

        key = 'wsq:query_by_id:{id}'.format(
            id=hashlib.md5(str(query.id).encode('UTF-8')).hexdigest(),
        )
        await self._redis.set(key, raw_value, ex=ttl)

    def _entity_to_bytes(self, entity: SearchQueryEntity) -> bytes:
        return pickle.dumps(entity)

    def _bytes_to_entity(self, value: Optional[bytes]) -> SearchQueryEntity:
        if value is not None:
            return pickle.loads(value)

        return None
