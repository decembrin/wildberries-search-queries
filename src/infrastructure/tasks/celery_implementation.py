import asyncio
from datetime import date
from typing import Optional

from celery import shared_task
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
    'CeleryTaskFactory',
]


@shared_task(bind=True, max_retries=14)
@inject
def download_report_task(
    self,
    period: ReportPeriod,
    task_service: ITaskService = Provide['task_service'],
    search_query_report_gateway: ISearchQueryReportGateway = Provide['search_query_report_gateway'],
):
    report_file_path = download_report_file(search_query_report_gateway, period)

    task_service.fetch_search_queries(
        report_file_path=report_file_path,
        period=period,
    )


@shared_task(bind=True)
@inject
def fetch_search_queries_task(
    self,
    report_file_path: str,
    period: ReportPeriod,
    task_service: ITaskService = Provide['task_service'],
):
    day = calendarutil.now().date()
    print(report_file_path)

    asyncio.run(
        process_report_file(report_file_path, day, period)
    )

    task_service.calculate_total_requests_per_day(day=day)


@shared_task(bind=True, max_retries=14)
def calculate_total_requests_per_day_task(
    self,
    day: date,
):
    asyncio.run(
        calculate_total_requests_per_day(day)
    )


class CeleryFetchSearchQueriesTask(ITask):
    def execute(self, report_file_path: str, period: ReportPeriod) -> None:
        fetch_search_queries_task.delay(report_file_path, period)


class CeleryDownloadReportTask(ITask):
    def __init__(self, period: ReportPeriod):
        self._period = period

    def execute(self):
        download_report_task.delay(self._period)


class CeleryCalculateTotalRequestsPerDayTask(ITask):
    def execute(self, day: date):
        calculate_total_requests_per_day_task.delay(day=day)


class CeleryTaskFactory(ITaskFactory):
    def create_task(self, task_name: str) -> Optional[ITask]:
        if task_name == 'download_one_week_report':
            return CeleryDownloadReportTask(ReportPeriod.ONE_WEEK)
        if task_name == 'download_one_month_report':
            return CeleryDownloadReportTask(ReportPeriod.ONE_MONTH)
        if task_name == 'download_three_month_report':
            return CeleryDownloadReportTask(ReportPeriod.THREE_MONTHS)
        if task_name == 'fetch_search_queries':
            return CeleryFetchSearchQueriesTask()
        if task_name == 'calculate_total_requests_per_day':
            return CeleryCalculateTotalRequestsPerDayTask()

        return
