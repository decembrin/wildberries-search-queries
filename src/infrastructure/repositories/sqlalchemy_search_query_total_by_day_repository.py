from datetime import date
from typing import List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import asc, between, func, select

from application.interfaces.search_query_total_by_day_repository_interface import (
    ISearchQueryTotalByDayRepository,
)

from .sqlalchemy_constants import (
    REQUESTS_TOTAL_BY_DAY_TABLE_NAME, SEARCH_QUERY_DAILY_STATS_TABLE_NAME,
)
from .sqlalchemy_orm import TableFactory


class SQLAlchemySearchQueryTotalByDayRepository(ISearchQueryTotalByDayRepository):
    def __init__(self, session):
        self._table_factory = TableFactory()
        self.session = session

    async def list(
        self,
        from_date: date,
        to_date: date,
    ) -> List[dict]:
        search_query_total_by_day_table = self._table_factory.create_table(REQUESTS_TOTAL_BY_DAY_TABLE_NAME)

        query = (
            select(
                search_query_total_by_day_table.c.day,
                search_query_total_by_day_table.c.total_requests_per_week,
            )
            .where(
                (between(search_query_total_by_day_table.c.day, from_date, to_date))
            )
            .select_from(search_query_total_by_day_table)
            .order_by(asc(search_query_total_by_day_table.c.day))
        )

        async with self.session() as session:
            return [{
                'day': row.day,
                'total_number_per_week': row.total_requests_per_week,
            } for row in await session.execute(query)]


    async def calculate_total_requests_per_day(self, day: date) -> None:
        requests_total_by_day_table = self._table_factory.create_table(REQUESTS_TOTAL_BY_DAY_TABLE_NAME)
        search_query_daily_stat_table = self._table_factory.create_table(SEARCH_QUERY_DAILY_STATS_TABLE_NAME)

        query = (
            insert(requests_total_by_day_table)
            .values({
                'day': day,
                'total_requests_per_week': (
                    select(
                        func.sum(search_query_daily_stat_table.c.requests_per_week)
                    )
                    .select_from(search_query_daily_stat_table)
                    .where(
                        (search_query_daily_stat_table.c.day == day)
                    )
                    .scalar_subquery()
                ),
            })
            .on_conflict_do_update(
                constraint=requests_total_by_day_table.UNIQUE_KEY_NAME,
                set_={
                    'day': requests_total_by_day_table.c.day,
                },
            )
        )
        async with self.session() as session:
            await session.execute(query)
            await session.commit()
