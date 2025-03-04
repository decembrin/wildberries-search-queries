from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.entities.search_query_entity import SearchQueryEntity


class ISearchQueryRepository(ABC):
    @abstractmethod
    def list(
        self,
        search_query_ids: Optional[List[int]] = None,
        search: Optional[str] = None,
        target_day: Optional[date] = None,
        sort_by: str = 'day',
        sort_dir: str = 'desc',
        limit: int = 100,
        offset: int = 0,
    ) -> List[SearchQueryEntity]:
        ...
    
    @abstractmethod
    async def bulk_create(
        self,
        values_list: List[SearchQueryEntity],
    ) -> None:
        ...

    @abstractmethod
    async def get_query_by_value(self) -> Optional[SearchQueryEntity]:
        ...
