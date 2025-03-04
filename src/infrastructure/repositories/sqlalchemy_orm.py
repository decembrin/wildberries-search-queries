from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Column, Table
from sqlalchemy.orm import registry
from sqlalchemy.schema import (
    Column, ForeignKey, Index, PrimaryKeyConstraint, UniqueConstraint,
)
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy_utils.types import TSVectorType

from application.utils import calendarutil

from .sqlalchemy_constants import *
from .sqlalchemy_types import *

mapper_registry = registry()



def create_search_query_table() -> Table:
    table = Table(
        SEARCH_QUERY_TABLE_NAME,
        mapper_registry.metadata,
        Column('id', BigIntegerType(), primary_key=True, autoincrement=True),
        Column('value', TextType(), default='', server_default=sa.text('\'\'::character varying')),
        Column('doc', TSVectorType(), default='', server_default=sa.text('\'\'::tsvector')),
        PrimaryKeyConstraint('id', name='searchquery_pkey'),
        UniqueConstraint('value', name=SEARCH_QUERY_TABLE_UNIQUE_KEY_NAME),
        Index('searchquery_id_idx', asc('id').nulls_last()),
        Index('searchquery_id_value_idx', 'id', 'value', postgresql_using='gist'),
        Index('searchquery_doc_idx', 'doc', postgresql_using='gin'),
    )
    table.UNIQUE_KEY_NAME = SEARCH_QUERY_TABLE_UNIQUE_KEY_NAME

    return table


def create_search_query_daily_stat_table() -> Table:
    table = Table(
        SEARCH_QUERY_DAILY_STATS_TABLE_NAME,
        mapper_registry.metadata,
        Column('id', BigIntegerType(), primary_key=True, autoincrement=True),
        Column('day', DateType(), primary_key=True, default=calendarutil.now, server_default=sa.text('date_trunc(\'day\', now())::date'), nullable=False),
        Column('requests_per_week', IntegerType(), default=0, server_default=sa.text('\'0\'::int'), nullable=False),
        Column('searchquery_id', ForeignKey('searchquery.id', name='searchquerydailystat_searchquery_id_fkey'), nullable=False),
        PrimaryKeyConstraint('id', 'day', name=f'searchquerydailystat_pkey'),
        UniqueConstraint('day', 'searchquery_id', name=SEARCH_QUERY_DAILY_STATS_TABLE_NAME),
        Index('searchquerydailystat_id_idx', asc('id').nulls_last()),
        Index('searchquerydailystat_day_idx', asc('day').nulls_last()),
        Index('searchquerydailystat_requests_per_week_day_idx', desc('requests_per_week').nulls_first(), asc('day').nulls_last()),
        postgresql_partition_by='RANGE (day)',
    )
    table.UNIQUE_KEY_NAME = SEARCH_QUERY_DAILY_STATS_TABLE_NAME

    return table


def create_search_query_daily_stat_tpl_table() -> Table:
    table = Table(
        SEARCH_QUERY_DAILY_STATS_TPL_TABLE_NAME,
        mapper_registry.metadata,
        Column('id', BigIntegerType(), primary_key=True, autoincrement=True),
        Column('day', DateType(), primary_key=True, default=calendarutil.now, server_default=sa.text('date_trunc(\'day\', now())::date'), nullable=False),
        Column('requests_per_week', IntegerType(), default=0, server_default=sa.text('\'0\'::int'), nullable=False),
        Column('searchquery_id', ForeignKey('searchquery.id', name='searchquerydailystat_tpl_searchquery_id_fkey'), nullable=False),
        PrimaryKeyConstraint('id', 'day', name='searchquerydailystat_tpl_pkey'),
        UniqueConstraint('day', 'searchquery_id', name=SEARCH_QUERY_DAILY_STATS_TPL_TABLE_UNIQUE_KEY),
        Index('searchquerydailystat_tpl_id_idx', asc('id').nulls_last()),
        Index('searchquerydailystat_tpl_day_idx', asc('day').nulls_last()),
        Index('searchquerydailystat_tpl_requests_per_week_day_idx', desc('requests_per_week').nulls_first(), asc('day').nulls_last()),
        postgresql_partition_by='RANGE (day)',
    )
    table.UNIQUE_KEY_NAME = SEARCH_QUERY_DAILY_STATS_TPL_TABLE_UNIQUE_KEY

    return table


def create_requests_total_by_day_table() -> Table:
    table = Table(
        REQUESTS_TOTAL_BY_DAY_TABLE_NAME,
        mapper_registry.metadata,
        Column('id', BigIntegerType(), primary_key=True, autoincrement=True),
        Column('day', DateType(), default=calendarutil.now, server_default=sa.text('date_trunc(\'day\', now())::date'), nullable=False),
        Column('total_requests_per_week', IntegerType(), default=0, server_default=sa.text('\'0\'::int'), nullable=False),
        PrimaryKeyConstraint('id', name='requeststotalbyday_pkey'),
        UniqueConstraint('day', name=REQUESTS_TOTAL_BY_DAY_TABLE_UNIQUE_KEY_NAME),
        Index('requeststotalbyday_id_idx', asc('id').nulls_last()),
        Index('requeststotalbyday_day_idx', 'day', asc('day').nulls_last()),
    )
    table.UNIQUE_KEY_NAME = REQUESTS_TOTAL_BY_DAY_TABLE_UNIQUE_KEY_NAME

    return table


class TableFactory:
    def create_table(self, name: str) -> Optional[Table]:
        if name in mapper_registry.metadata.tables:
            return mapper_registry.metadata.tables[name]

        if name == SEARCH_QUERY_TABLE_NAME:
            return create_search_query_table()
        if name == SEARCH_QUERY_DAILY_STATS_TABLE_NAME:
            return create_search_query_daily_stat_table()
        if name == SEARCH_QUERY_DAILY_STATS_TPL_TABLE_NAME:
            return create_search_query_daily_stat_tpl_table()
        if name == REQUESTS_TOTAL_BY_DAY_TABLE_NAME:
            return create_requests_total_by_day_table()


def init_default_tables():
    table_factory = TableFactory()
    table_factory.create_table(SEARCH_QUERY_TABLE_NAME)
    table_factory.create_table(SEARCH_QUERY_DAILY_STATS_TABLE_NAME)
    table_factory.create_table(SEARCH_QUERY_DAILY_STATS_TPL_TABLE_NAME)
    table_factory.create_table(REQUESTS_TOTAL_BY_DAY_TABLE_NAME)


'''
SELECT partman.create_parent(
    p_parent_table := 'public.searchquerydailystat'
    , p_control := 'day'
    , p_interval := '1 month'
    , p_template_table := 'public.searchquerydailystat_tpl'
);
'''