from abc import ABC, abstractmethod
from datetime import date
from typing import List


class ISearchQueryTotalByDayRepository(ABC):
    @abstractmethod
    async def list(
        self,
        from_date: date,
        to_date: date,
    ) -> List[dict]:
        ...

    @abstractmethod
    async def calculate_total_requests_per_day(
        self,
        day: date,
    ) -> None:
        ...
