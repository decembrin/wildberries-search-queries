from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(kw_only=True)
class SearchQueryDailyStatsEntity:
    id: Optional[int] = None
    day: date
    value: str
    requests_per_week: Optional[int] = None
    searchquery_id: int
