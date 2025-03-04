from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from dateutil.relativedelta import relativedelta

from application.interfaces.search_query_cache_interface import (
    ISearchQueryCache,
)
from application.utils import calendarutil
from domain.entities.search_query_entity import SearchQueryEntity


@dataclass
class CacheObject:
    created_at: datetime
    ttl: Optional[int] = None
    entity: Optional[Any] = None


def check_ttl(func):
    def wrapper(*args, **kwargs):
        cache_object = func(*args, **kwargs)

        now = calendarutil.now()
        if (cache_object is not None
            and cache_object.ttl is not None
            and cache_object.created_at + relativedelta(seconds=cache_object.ttl) < now
        ):
            return None

        return cache_object

    return wrapper


class MemorySearchQueryCache(ISearchQueryCache):
    _query_cache_object_by_id: Dict[int, CacheObject]
    _query_cache_object_by_value: Dict[str, CacheObject]

    def __init__(self):
        self._query_cache_object_by_id = {}
        self._query_cache_object_by_value = {}

    async def get_query_by_id(self, query_id: int) -> Optional[SearchQueryEntity]:
        if query_cache_object := self._get_query_cache_object_by_id(query_id):
            return query_cache_object.entity

        return None

    async def get_query_by_value(self, query_value: int) -> Optional[SearchQueryEntity]:
        if query_cache_object := self._get_query_cache_object_by_value(query_value):
            return query_cache_object.entity

        return None

    async def save_search_query(self, query: SearchQueryEntity, ttl: int = None) -> None:
        if query is None:
            return
 
        cache_object = CacheObject(
            created_at=datetime.now(tz=timezone.utc),
            entity=query,
            ttl=ttl,
        )
        # Сохраняем ссылку на CacheObject в _query_cache_object_by_id
        self._query_cache_object_by_id[query.id] = cache_object
        # Сохраняем ссылку на CacheObject в _query_cache_object_by_value
        self._query_cache_object_by_value[query.value] = cache_object

    @check_ttl
    def _get_query_cache_object_by_id(self, query_id: int) -> Optional[CacheObject]:
        return self._query_cache_object_by_id.get(query_id)

    @check_ttl
    def _get_query_cache_object_by_value(self, query_value: int) -> Optional[CacheObject]:
        return self._query_cache_object_by_value.get(query_value)
