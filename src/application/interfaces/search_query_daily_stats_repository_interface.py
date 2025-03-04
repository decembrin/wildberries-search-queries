from abc import ABC, abstractmethod
from datetime import date
from typing import List

from domain.entities.search_query_daily_stats_entity import (
    SearchQueryDailyStatsEntity,
)


class ISearchQueryDailyStatsRepository(ABC):
    @abstractmethod
    async def list(
        self,
        search_query_ids: List[int],
        from_date: date,
        to_date: date,
    ) -> List[SearchQueryDailyStatsEntity]:
        ...

    @abstractmethod
    async def bulk_create(
        self,
        insert_obj_list: List[dict],
    ) -> None:
        ...
