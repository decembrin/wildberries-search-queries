from dependency_injector.wiring import Provide, inject

from application.use_cases import (
    FindSearchQueriesUseCase, FindSearchQueryDailyStatsUseCase,
)
from containers import Container

__all__ = [
    'provide_download_search_query_report_use_case',
    'provide_find_search_queies_use_case',
    'provide_find_search_query_daily_stats_use_case',
    'provide_find_total_requests_per_day_use_case',
]


@inject
async def provide_download_search_query_report_use_case(
    download_search_query_report_use_case = Provide[Container.download_search_query_report_use_case],
):
    return download_search_query_report_use_case


@inject
async def provide_find_search_queies_use_case(
    find_search_queies_use_case = Provide[Container.find_search_queies_use_case],
) -> FindSearchQueriesUseCase:
    return find_search_queies_use_case


@inject
async def provide_find_search_query_daily_stats_use_case(
    find_search_query_daily_stats_use_case = Provide[Container.find_search_query_daily_stats_use_case],
) -> FindSearchQueryDailyStatsUseCase:
    return find_search_query_daily_stats_use_case


@inject
async def provide_find_total_requests_per_day_use_case(
    find_total_requests_per_day_use_case = Provide[Container.find_total_requests_per_day_use_case],
):
    return find_total_requests_per_day_use_case
