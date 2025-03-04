from datetime import date
from typing import List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import asc, between, select

from application.interfaces.search_query_daily_stats_repository_interface import (
    ISearchQueryDailyStatsRepository,
)
from domain.entities.search_query_daily_stats_entity import (
    SearchQueryDailyStatsEntity,
)

from .sqlalchemy_constants import (
    SEARCH_QUERY_DAILY_STATS_TABLE_NAME, SEARCH_QUERY_TABLE_NAME,
)
from .sqlalchemy_orm import TableFactory


class SQLAlchemySearchQueryDailyStatsRepository(ISearchQueryDailyStatsRepository):
    def __init__(self, session):
        self._table_factory = TableFactory()
        self._session = session

    async def list(
        self,
        search_query_ids: List[int],
        from_date: date,
        to_date: date,
    ) -> List[SearchQueryDailyStatsEntity]:
        search_query_table = self._table_factory.create_table(SEARCH_QUERY_TABLE_NAME)
        search_query_daily_stat_table = self._table_factory.create_table(SEARCH_QUERY_DAILY_STATS_TABLE_NAME)

        query = (
            select(
                search_query_daily_stat_table.c.id,
                search_query_daily_stat_table.c.day,
                search_query_table.c.value,
                search_query_daily_stat_table.c.requests_per_week,
                search_query_table.c.id,
            )
            .select_from(search_query_daily_stat_table)
            .join(search_query_table, search_query_table.c.id == search_query_daily_stat_table.c.searchquery_id)
            .where(
                  (search_query_daily_stat_table.c.searchquery_id.in_(search_query_ids))
                & (between(search_query_daily_stat_table.c.day, from_date, to_date))
            )
            .order_by(asc(search_query_daily_stat_table.c.day))
        )

        async with self._session() as session:
            return [
                SearchQueryDailyStatsEntity(
                    id=row[0],
                    day=row[1],
                    value=row[2],
                    requests_per_week=row[3],
                    searchquery_id=row[4],
                ) for row in await session.execute(query)
            ]

    async def bulk_create(self, insert_obj_list: List[dict]) -> None:
        table = self._table_factory.create_table(SEARCH_QUERY_DAILY_STATS_TABLE_NAME)

        if not insert_obj_list:
            return

        update_columns = {}

        first_insert_obj = insert_obj_list[0]
        if first_insert_obj['requests_per_week'] is not None:
            update_columns['requests_per_week'] = table.c.requests_per_week

        stmt = (
            insert(table)
            .values(insert_obj_list)
            .on_conflict_do_update(
                constraint=table.UNIQUE_KEY_NAME,
                set_=update_columns,
            )
        )
        async with self._session() as session:
            await session.execute(stmt)
            await session.commit()
