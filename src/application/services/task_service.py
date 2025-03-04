from datetime import date

from domain.enums.report_period_enum import ReportPeriod
from domain.interfaces.task_factory_interface import ITaskFactory
from domain.interfaces.task_service_interface import ITaskService


class TaskService(ITaskService):
    def __init__(self, task_factory: ITaskFactory) -> None:
        self._task_factory = task_factory

    def download_search_query_report(self, period: ReportPeriod = ReportPeriod.ONE_WEEK) -> None:
        if period == ReportPeriod.ONE_WEEK:
            task = self._task_factory.create_task('download_one_week_report')
            task.execute()
        elif period == ReportPeriod.ONE_MONTH:
            task = self._task_factory.create_task('download_one_month_report')
            task.execute()
        elif period == ReportPeriod.THREE_MONTHS:
            task = self._task_factory.create_task('download_three_months_report')
            task.execute()

    def fetch_search_queries(self, report_file_path: str, period: ReportPeriod) -> None:
        task = self._task_factory.create_task('fetch_search_queries')
        task.execute(report_file_path, period)

    def calculate_total_requests_per_day(self, day: date) -> None:
        task = self._task_factory.create_task('calculate_total_requests_per_day')
        task.execute(day)
