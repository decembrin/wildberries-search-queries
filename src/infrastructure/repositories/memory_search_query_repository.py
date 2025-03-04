from typing import List, Optional

from application.interfaces.search_query_repository_interface import (
    ISearchQueryRepository,
)
from domain.entities.search_query_entity import SearchQueryEntity


class MemorySearchQueryRepository(ISearchQueryRepository):
    def __init__(self) -> None:
        self._storage = {}

    async def bulk_create(self, values_list: List[SearchQueryEntity]) -> None:
        for search_query in values_list:
            self._storage[search_query.id] = search_query

    async def list(self) -> List[SearchQueryEntity]:
        return sorted(self._storage.values(), key=lambda x: x.id)

    async def get_query_by_value(self, query_value: str) -> Optional[SearchQueryEntity]:
        for query in self._storage.values():
            if query.value == query_value:
                return query

        return None
