import asyncio
import time
from datetime import date
from typing import Optional

from dependency_injector.wiring import Provide, inject

from application.utils import calendarutil
from domain.enums.report_period_enum import ReportPeriod
from domain.interfaces.search_query_report_gateway_interface import (
    ISearchQueryReportGateway,
)
from domain.interfaces.task_factory_interface import ITaskFactory
from domain.interfaces.task_interface import ITask
from domain.interfaces.task_service_interface import ITaskService

from .utils import (
    calculate_total_requests_per_day, download_report_file,
    process_report_file,
)

__all__ = [
    'SyncTaskFactory',
]


@inject
def download_report_task(
    period: ReportPeriod,
    task_service: ITaskService = Provide['task_service'],
    search_query_report_gateway: ISearchQueryReportGateway = Provide['search_query_report_gateway'],
):
    report_file_path = download_report_file(search_query_report_gateway, period)

    task_service.fetch_search_queries(
        report_file_path=report_file_path,
        period=period,
    )


@inject
def fetch_search_queries_task(
    report_file_path: str,
    period: ReportPeriod,
    # task_service: ITaskService = Provide['task_service'],
):
    day = calendarutil.now().date()

    loop = asyncio.get_running_loop()
    loop.run_until_complete(asyncio.create_task(
        process_report_file(report_file_path, day, period)
    ))

    # task_service.calculate_total_requests_per_day(day=day)


def calculate_total_requests_per_day_task(
    day: date,
):
    loop = asyncio.get_event_loop()
    task = loop.create_task(calculate_total_requests_per_day(day))

    loop.run_until_complete(
        task
    )


class SyncFetchSearchQueriesTask(ITask):
    def execute(self, report_file_path: str, period: ReportPeriod) -> None:
        fetch_search_queries_task(report_file_path, period)


class SyncDownloadReportTask(ITask):
    def __init__(self, period: ReportPeriod):
        self._period = period

    def execute(self):
        download_report_task(self._period)


class SyncCalculateTotalRequestsPerDayTask(ITask):
    def execute(self, day: date):
        calculate_total_requests_per_day_task(day=day)


class SyncTaskFactory(ITaskFactory):
    def create_task(self, task_name: str) -> Optional[ITask]:
        if task_name == 'download_one_week_report':
            return SyncDownloadReportTask(ReportPeriod.ONE_WEEK)
        if task_name == 'download_one_month_report':
            return SyncDownloadReportTask(ReportPeriod.ONE_MONTH)
        if task_name == 'download_three_month_report':
            return SyncDownloadReportTask(ReportPeriod.THREE_MONTHS)
        if task_name == 'fetch_search_queries':
            return SyncFetchSearchQueriesTask()
        if task_name == 'calculate_total_requests_per_day':
            return SyncCalculateTotalRequestsPerDayTask()

        return