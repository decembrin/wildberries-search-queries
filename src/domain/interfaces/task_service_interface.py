from abc import ABC, abstractmethod
from datetime import date

from domain.enums.report_period_enum import ReportPeriod


class ITaskService(ABC):
    @abstractmethod
    def download_search_query_report(self, period: ReportPeriod = ReportPeriod.ONE_WEEK) -> None:
        ...

    @abstractmethod
    def fetch_search_queries(self, report_file_path: str) -> None:
        ...

    @abstractmethod
    def calculate_total_requests_per_day(self, day: date) -> None:
        ...
