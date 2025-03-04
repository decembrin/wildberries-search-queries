from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class SearchQueryEntity:
    id: Optional[int] = None
    value: str
