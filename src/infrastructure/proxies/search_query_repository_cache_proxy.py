from datetime import date
from typing import List, Optional

from application.interfaces.search_query_cache_interface import (
    ISearchQueryCache,
)
from application.interfaces.search_query_repository_interface import (
    ISearchQueryRepository,
)
from domain.entities.search_query_entity import SearchQueryEntity


class SearchQueryRepositoryCacheProxy(ISearchQueryRepository):
    def __init__(
        self,
        search_query_repository: ISearchQueryRepository,
        search_query_cache: ISearchQueryCache,
    ) -> None:
        self._search_query_repository = search_query_repository
        self._search_query_cache = search_query_cache

    async def list(
        self,
        search_query_ids: Optional[List[int]] = None,
        search: Optional[str] = None,
        target_day: Optional[date] = None,
        sort_by: str = 'day',
        sort_dir: str = 'desc',
        limit: int = 100,
        offset: int = 0,
    ) -> List[SearchQueryEntity]:
        return await self._search_query_repository.list(
            search_query_ids=search_query_ids,
            search=search,
            target_day=target_day,
            sort_by=sort_by,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )

    async def get_query_by_value(self, query_value: str) -> Optional[SearchQueryEntity]:
        if query := await self._search_query_cache.get_query_by_value(query_value):
            return query

        query = await self._search_query_repository.get_query_by_value(query_value)

        await self._search_query_cache.save_search_query(query)

        return query
    
    async def bulk_create(self, values_list: List[SearchQueryEntity]) -> None:
        await self._search_query_repository.bulk_create(values_list)

        for search_query in values_list:
            await self._search_query_cache.save_search_query(search_query)
