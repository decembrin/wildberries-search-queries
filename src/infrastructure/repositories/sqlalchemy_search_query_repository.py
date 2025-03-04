from datetime import date
from typing import List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import asc, desc, select

from application.interfaces.search_query_repository_interface import (
    ISearchQueryRepository,
)
from domain.entities.search_query_entity import SearchQueryEntity

from .sqlalchemy_constants import (
    SEARCH_QUERY_DAILY_STATS_TABLE_NAME, SEARCH_QUERY_TABLE_NAME,
)
from .sqlalchemy_orm import TableFactory


class SQLAlchemySearchQueryRepository(ISearchQueryRepository):
    def __init__(self, session):
        self._table_factory = TableFactory()
        self.session = session

    async def bulk_create(self, values_list: List[SearchQueryEntity]) -> None:
        table = self._table_factory.create_table(SEARCH_QUERY_TABLE_NAME)

        inserted_data = []
        index_by_value = {}
        for i, search_query in enumerate(values_list):
            index_by_value[search_query.value] = i
            inserted_data.append({
                'value': search_query.value,
            })

        stmt = (
            insert(table)
            .values(inserted_data)
            .on_conflict_do_update(
                constraint=table.UNIQUE_KEY_NAME,
                set_={
                    'value': table.c.value,
                },
            )
            .returning(table.c.id, table.c.value)
        )
        async with self.session() as session:
            returning_values = await session.execute(stmt)
            await session.commit()

        for search_query_id, search_query_value in returning_values:
            search_query = values_list[index_by_value[search_query_value]]
            search_query.id = search_query_id

    async def get_query_by_value(self, value: str) -> Optional[SearchQueryEntity]:
        return None

    async def list(
        self,
        search_query_ids: Optional[List[int]] = None,
        search: Optional[str] = None,
        target_day: Optional[date] = None,
        sort_by: str = 'day',
        sort_dir: str = 'desc',
        limit: int = 100,
        offset: int = 0,
    ) -> List[SearchQueryEntity]:
        search_query_table = self._table_factory.create_table(SEARCH_QUERY_TABLE_NAME)
        search_query_daily_stat_table = self._table_factory.create_table(SEARCH_QUERY_DAILY_STATS_TABLE_NAME)

        query = (
            select(
                search_query_table.c.id,
                search_query_table.c.value,
            )
            .select_from(search_query_table)
            .limit(limit)
        )

        if sort_by == 'day':
            if target_day is None:
                raise Exception('target_day is not None')

            query = (
                query
                .join(search_query_daily_stat_table, search_query_daily_stat_table.c.searchquery_id == search_query_table.c.id)
                .where(
                    (search_query_daily_stat_table.c.day == target_day)
                )
            )

            if sort_dir == 'asc':
                query = (
                    query.order_by(asc(search_query_daily_stat_table.c.requests_per_week))
                )
            else:
                query = (
                    query.order_by(desc(search_query_daily_stat_table.c.requests_per_week))
                )
        else:
            query = (
                query
                .order_by(asc(search_query_table.c.value))
            )
        if search_query_ids:
            query = (
                query.where(
                      (search_query_table.c.id.in_(search_query_ids))
                )
            )
        if search:
            query = (
                query.where(
                      (search_query_table.c.doc.match(search, postgresql_regconfig='russian'))
                    | (search_query_table.c.doc.match(search, postgresql_regconfig='english'))
                )
            )

        async with self.session() as session:
            return [
                SearchQueryEntity(
                    id=row[0],
                    value=row[1],
                ) for row in await session.execute(query)
            ]
