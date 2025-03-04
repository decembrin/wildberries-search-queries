from datetime import date
from typing import List, Optional

from dateutil.relativedelta import relativedelta

from application.interfaces.search_query_daily_stats_repository_interface import (
    ISearchQueryDailyStatsRepository,
)
from application.interfaces.search_query_total_by_day_repository_interface import (
    ISearchQueryTotalByDayRepository,
    ISearchQueryTotalByDayRepository as ISearchQueryTotalNumberPerDayRepository,
)
from application.utils import calendarutil
from domain.entities.search_query_entity import SearchQueryEntity
from domain.enums.report_period_enum import ReportPeriod


class BulkCreateSearchQueryDailyStatsUseCase:
    def __init__(
        self,
        search_query_daily_stats_repository: ISearchQueryDailyStatsRepository,
        get_search_query_by_value_use_case,
        bulk_create_search_queries_use_case,
    ) -> None:
        self._search_query_daily_stats_repository = search_query_daily_stats_repository
        self._get_search_query_by_value_use_case = get_search_query_by_value_use_case
        self._bulk_create_search_queries_use_case = bulk_create_search_queries_use_case

    async def execute(
        self,
        values: List[tuple],
        day: date,
        period: ReportPeriod,
    ) -> list:
        index_by_search_query_value = {}
        inserted_search_query = []
        inserted_daily_stat_data = []

        for i, (search_query_value, number_of_requests) in enumerate(values):
            search_query = await self._get_search_query_by_value_use_case.execute(search_query_value)

            if search_query is None:
                search_query = SearchQueryEntity(
                    value=search_query_value,
                )

                inserted_search_query.append(search_query)

                index_by_search_query_value[search_query_value] = i

            search_query_daily_stat = {
                'day': day,
                'searchquery_id': search_query.id,
            }
            if period == ReportPeriod.ONE_WEEK:
                search_query_daily_stat['requests_per_week'] = int(number_of_requests)

            inserted_daily_stat_data.append(search_query_daily_stat)

        if inserted_search_query:
            await self._bulk_create_search_queries_use_case.execute(inserted_search_query)

        for search_query in inserted_search_query:
            search_query_daily_stat = inserted_daily_stat_data[index_by_search_query_value[search_query.value]]
            search_query_daily_stat['searchquery_id'] = search_query.id

        await self._search_query_daily_stats_repository.bulk_create(inserted_daily_stat_data)


class FindSearchQueryDailyStatsUseCase:
    def __init__(
        self,
        search_query_daily_stat_repository: ISearchQueryDailyStatsRepository,
    ) -> None:
        self._search_query_daily_stat_repository = search_query_daily_stat_repository

    async def execute(
        self,
        search_query_ids: List[int],
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list:
        now = calendarutil.now()
        if to_date is None:
            to_date = now.date()

        if from_date is None:
            from_date = to_date - relativedelta(days=14)

        return await self._search_query_daily_stat_repository.list(
            search_query_ids=search_query_ids,
            from_date=from_date,
            to_date=to_date,
        )
 

class CalculateTotalRequestsPerDayUseCase:
    def __init__(
        self,
        search_query_total_number_per_day_repository: ISearchQueryTotalByDayRepository,
    ) -> None:
        self._search_query_total_number_per_day_repository = search_query_total_number_per_day_repository

    async def execute(
        self,
        day: date,
    ) -> list:
        await self._search_query_total_number_per_day_repository.calculate_total_requests_per_day(day)


class FindTotalRequestsPerDayUseCase:
    def __init__(
        self,
        search_query_total_number_per_day_repository: ISearchQueryTotalNumberPerDayRepository,
    ) -> None:
        self._search_query_total_number_per_day_repository = search_query_total_number_per_day_repository

    async def execute(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list:
        now = calendarutil.now()
        if to_date is None:
            to_date = now.date()

        if from_date is None:
            from_date = to_date - relativedelta(days=14)

        return await self._search_query_total_number_per_day_repository.list(
            from_date=from_date,
            to_date=to_date,
        )
