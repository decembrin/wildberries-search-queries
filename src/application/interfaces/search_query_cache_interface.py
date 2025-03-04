from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.search_query_entity import SearchQueryEntity


class ISearchQueryCache(ABC):
    @abstractmethod
    async def get_query_by_id(self, query_id: int) -> Optional[SearchQueryEntity]:
        ...

    @abstractmethod
    async def get_query_by_value(self, query_value: int) -> Optional[SearchQueryEntity]:
        ...

    @abstractmethod
    async def save_search_query(self, query: SearchQueryEntity, ttl: int = None) -> None:
        ...
