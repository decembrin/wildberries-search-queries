from abc import ABC, abstractmethod

from domain.enums.report_period_enum import ReportPeriod


class ISearchQueryReportGateway(ABC):
    @abstractmethod
    def download_report(self, period: ReportPeriod = ReportPeriod.ONE_WEEK):
        pass
