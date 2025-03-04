from typing import List, Optional

import dateutil

from application.interfaces.search_query_cache_interface import (
    ISearchQueryCache,
)
from application.interfaces.search_query_repository_interface import (
    ISearchQueryRepository,
)
from application.utils import calendarutil
from domain.entities.search_query_entity import SearchQueryEntity
from domain.enums.report_period_enum import ReportPeriod
from domain.interfaces.task_service_interface import ITaskService


class DownloadSearchQueryReportUseCase:
    """
    Use Case для загрузки отчета по поисковым запросам.

    Атрибуты:
        task_service (ITaskService): Сервис задач, используемый для загрузки отчета.

    Методы:
        execute(period: ReportPeriod) -> None:
            Запускает задачу загрузки отчета по поисковым запросам за указанный период.
    """
    def __init__(self, task_service: ITaskService) -> None:
        self._task_service = task_service

    async def execute(self, period: ReportPeriod) -> None:
        self._task_service.download_search_query_report(period)


class BulkCreateSearchQueriesUseCase:
    def __init__(self, search_query_repository: ISearchQueryRepository) -> None:
        self._search_query_repository = search_query_repository

    async def execute(
        self,
        values_list: List[SearchQueryEntity],
    ) -> Optional[List[SearchQueryEntity]]:
        await self._search_query_repository.bulk_create(values_list)


class FindSearchQueriesUseCase:
    def __init__(self, search_query_repository: ISearchQueryRepository) -> None:
        self._search_query_repository = search_query_repository

    async def execute(
        self,
        search_query_ids: Optional[List[int]] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_dir: str = 'desc',
        limit: int = 1000,
        offset: int = 0,
    ) -> List[SearchQueryEntity]:
        if sort_by is not None and sort_by.startswith('day/'):
            sort_by, date_string = sort_by.split('/')
            try:
                target_day = dateutil.parser.parse(date_string)
            except Exception:
                target_day = calendarutil.now().date()
        else:
            sort_by = 'value'
            target_day = None

        return await self._search_query_repository.list(
            search_query_ids=search_query_ids,
            search=search,
            target_day=target_day,
            sort_by=sort_by,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )


class GetSearchQueryByValueUseCase:
    def __init__(
        self,
        search_query_repository: ISearchQueryRepository,
        search_query_cache: ISearchQueryCache,
    ) -> None:
        self._search_query_repository = search_query_repository
        self._search_query_cache = search_query_cache

    async def execute(
        self,
        value: str,
    ) -> Optional[SearchQueryEntity]:
        if search_query := await self._search_query_cache.get_query_by_value(value):
            return search_query

        return await self._search_query_repository.get_query_by_value(value)
