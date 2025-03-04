
from datetime import date
from typing import List, Optional

from fastapi import Depends, Query
from fastapi.routing import APIRouter

from application.use_cases import (
    FindSearchQueriesUseCase, FindSearchQueryDailyStatsUseCase,
    FindTotalRequestsPerDayUseCase,
)

from ..dependencies import (
    provide_find_search_queies_use_case,
    provide_find_search_query_daily_stats_use_case,
    provide_find_total_requests_per_day_use_case,
)

router = APIRouter()


@router.get('/')
async def get_search_query_daily_stats(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search_query_ids: List[int] = Query(default=[], alias='search_query_id'),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_dir: str = 'desc',
    limit: int = 100,
    offset: int = 0,
    find_search_queries_use_case: FindSearchQueriesUseCase = Depends(provide_find_search_queies_use_case),
    find_search_query_daily_stats_use_case: FindSearchQueryDailyStatsUseCase = Depends(provide_find_search_query_daily_stats_use_case),
) -> None:
    search_queries = await find_search_queries_use_case.execute(
        search_query_ids=search_query_ids,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )

    result = []
    search_query_index_by_id = {}
    for i, search_query in enumerate(search_queries):
        search_query_index_by_id[search_query.id] = i

        result.append({
            'id': search_query.id,
            'text': search_query.value,
            'statistics': [],
        })

    daily_search_query_stats = await find_search_query_daily_stats_use_case.execute(
        from_date=from_date,
        to_date=to_date,
        search_query_ids=list(search_query_index_by_id.keys()),
    )

    for stats in daily_search_query_stats:
        result_index = search_query_index_by_id[stats.searchquery_id]

        result[result_index]['statistics'].append({
            'date': stats.day,
            'requests_per_week': stats.requests_per_week,
        })

    return {
        'result': result,
    }


@router.get('/total-requests-per-day/')
async def get_total_requests_per_day_day(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    find_total_requests_per_day_use_case: FindTotalRequestsPerDayUseCase = Depends(provide_find_total_requests_per_day_use_case),
) -> dict:
    result = await find_total_requests_per_day_use_case.execute(
        from_date=from_date,
        to_date=to_date,
    )

    return {
        'result': [{
            'date': item['day'],
            'value': item['total_number_per_week'],
        } for item in result],
    }
