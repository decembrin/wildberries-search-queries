import io
from base64 import b64decode
from typing import Optional

import requests

from domain.enums.report_period_enum import ReportPeriod
from domain.interfaces.search_query_report_gateway_interface import (
    ISearchQueryReportGateway,
)


class WildberriesSearchQueryReportGateway(ISearchQueryReportGateway):
    def __init__(self, authorizev3: str, wbx_validation_key: str) -> None:
        self.authorizev3 = authorizev3
        self.wbx_validation_key = wbx_validation_key

    def download_report(self, period: ReportPeriod = ReportPeriod.ONE_WEEK) -> Optional[io.BytesIO]:
        with self.get_session() as session:
            r = session.get(
                url='https://seller-weekly-report.wildberries.ru/ns/trending-searches/suppliers-portal-analytics/file',
                params={
                    'period': period.value,
                },
            )
            if r.status_code == 200:
                response_data = r.json()

                data = response_data['data']['file']

                return io.BytesIO(b64decode(data))
            elif r.status_code in (401, 403):
                raise Exception('Unauthorized error') 
            else:
                raise Exception('Failed to download report')


    def get_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json',
            'Origin': 'https://seller.wildberries.ru',
            'Referer': 'https://seller.wildberries.ru/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'authorizev3': self.authorizev3,
        })
        session.cookies.set('wbx-validation-key', self.wbx_validation_key)

        return session
