from fastapi import Depends
from fastapi.routing import APIRouter

from application.use_cases.search_query_use_cases import (
    DownloadSearchQueryReportUseCase,
)
from domain.enums.report_period_enum import ReportPeriod

from ..dependencies import provide_download_search_query_report_use_case

router = APIRouter()


@router.post('/download_one_week_report/')
async def run_download_one_week_report_command(
    download_search_query_report_use_case: DownloadSearchQueryReportUseCase = Depends(provide_download_search_query_report_use_case)
) -> None:
    await download_search_query_report_use_case.execute(ReportPeriod.ONE_WEEK)
