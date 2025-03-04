import asyncio
import csv
import gzip
import os
import shutil
from datetime import date
from itertools import islice
from typing import List

from dependency_injector.wiring import Provide, inject

from application.utils import calendarutil
from domain.enums.report_period_enum import ReportPeriod
from domain.interfaces.search_query_report_gateway_interface import (
    ISearchQueryReportGateway,
)


def download_report_file(
    search_query_report_gateway: ISearchQueryReportGateway,
    period: ReportPeriod,
) -> str:
    now = calendarutil.now()
    report_folder_path = now.strftime(f'/tmp/reports/%Y/%m')
    report_file_path = now.strftime(f'{report_folder_path}/%Y-%m-%d_{period.name.lower()}_report.csv.gz')

    if not os.path.exists(report_file_path):
        os.makedirs(report_folder_path, exist_ok=True)

        file = search_query_report_gateway.download_report(period)

        with gzip.open(report_file_path, mode='wb') as f:
            shutil.copyfileobj(file, f)

    return report_file_path


@inject
async def process_report_file(
    report_file_path: str,
    day: date,
    period: ReportPeriod,
    bulk_create_search_query_daily_stats_use_case = Provide['bulk_create_search_query_daily_stats_use_case'],
):
    tasks_in_processing, lock = 0, asyncio.Lock() 

    semaphore = asyncio.BoundedSemaphore(8)

    async def report_file_reader(file_path: str):
        with gzip.open(file_path, mode='rt') as f:
            while True:
                chunk = list(islice(csv.reader(f), 1000))
                if not chunk:
                    break

                async with semaphore:
                    yield chunk
                # Переключаемся на выполнение задач
                await asyncio.sleep(0)

    async def report_processor(generator):
        nonlocal tasks_in_processing

        async for values_list in generator:
            try:
                asyncio.create_task(
                    bulk_create_task(
                        values_list=values_list,
                        day=day,
                        period=period,
                    )
                )
            finally:
                async with lock:
                    tasks_in_processing += 1

        # Ожидаем завершения всех bulk_create_task
        while tasks_in_processing:
            await asyncio.sleep(1) 

    async def bulk_create_task(
        values_list: List[tuple],
        day: date,
        period: ReportPeriod,
    ):
        nonlocal tasks_in_processing

        try:
            async with semaphore:
                await bulk_create_search_query_daily_stats_use_case.execute(
                    values=values_list,
                    day=day,
                    period=period,
                )
        except Exception as e:
            pass
        finally:
            async with lock:
                tasks_in_processing -= 1

    generator = report_file_reader(report_file_path)

    await report_processor(generator)


@inject
async def calculate_total_requests_per_day(
    day: date,
    calculate_total_requests_per_day_use_case = Provide['calculate_total_requests_per_day_use_case'],
):
    await calculate_total_requests_per_day_use_case.execute(day)
