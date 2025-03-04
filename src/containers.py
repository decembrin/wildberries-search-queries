from dependency_injector import containers, providers

from application.services import *
from application.use_cases import *
from config import Settings
from infrastructure.caches import *
from infrastructure.gateways import *
from infrastructure.proxies import *
from infrastructure.redis.client import init_redis_client
from infrastructure.repositories import *
from infrastructure.repositories.sqlalchemy_session import (
    init_sqlalchemy_async_session,
)
from infrastructure.tasks import *


class SearchQueryUseCasesContainer(containers.DeclarativeContainer):
    pass


class SearchQueryDailyStatsUseCasesContainer(containers.DeclarativeContainer):
    pass


class Container(containers.DeclarativeContainer):
    settings = Settings()

    config = providers.Configuration()
    config.from_dict(settings.model_dump(mode='json'))

    sqlalchemy_session = providers.Factory(
        init_sqlalchemy_async_session,
        url=config.postgres_url,
    )

    redis_client = providers.Resource(
        init_redis_client,
        url=config.redis_url,
    )

    sqlalchemy_search_query_repository = providers.Singleton(
        SQLAlchemySearchQueryRepository,
        session=sqlalchemy_session,
    )

    sqlalchemy_search_query_daily_stats_repository = providers.Singleton(
        SQLAlchemySearchQueryDailyStatsRepository,
        session=sqlalchemy_session,
    )

    sqlalchemy_search_query_total_by_day_repository = providers.Singleton(
        SQLAlchemySearchQueryTotalByDayRepository,
        session=sqlalchemy_session,
    )

    search_query_cache = providers.Singleton(
        RedisSearchQueryCache,
        redis_client=redis_client,
    )

    search_query_repository = providers.Singleton(
        SearchQueryRepositoryCacheProxy,
        search_query_repository=sqlalchemy_search_query_repository,
        search_query_cache=search_query_cache,
    )

    search_query_daily_stats_repository = sqlalchemy_search_query_daily_stats_repository

    search_query_total_by_day_repository = sqlalchemy_search_query_total_by_day_repository
    search_query_total_number_per_day_repository = search_query_total_by_day_repository # 00000000

    task_factory = providers.Singleton(
        CeleryTaskFactory,
    )

    task_service = providers.Singleton(
        TaskService,
        task_factory=task_factory,
    )

    search_query_report_gateway = providers.Singleton(
        WildberriesSearchQueryReportGateway,
        authorizev3=config.wb_authorizev3,
        wbx_validation_key=config.wb_wbx_validation_key,
    )

    # User Cases
    # search_query_use_cases = providers.Container(SearchQueryUseCasesContainer)
    # search_query_daily_stats_use_Ccses = providers.Container(SearchQueryDailyStatsUseCasesContainer)

    download_search_query_report_use_case = providers.Factory(
        DownloadSearchQueryReportUseCase,
        task_service=task_service,
    )

    bulk_create_search_queries_use_case = providers.Factory(
        BulkCreateSearchQueriesUseCase,
        search_query_repository=search_query_repository,
    )

    get_search_query_by_value_use_case = providers.Factory(
        GetSearchQueryByValueUseCase,
        search_query_repository=search_query_repository,
        search_query_cache=search_query_cache,
    )

    find_search_queies_use_case = providers.Factory(
        FindSearchQueriesUseCase,
        search_query_repository=search_query_repository,
    )

    find_search_query_daily_stats_use_case = providers.Factory(
        FindSearchQueryDailyStatsUseCase,
        search_query_daily_stats_repository
    )

    find_total_requests_per_day_use_case = providers.Factory(
        FindTotalRequestsPerDayUseCase,
        search_query_total_number_per_day_repository,
    )

    # Возможно не использовать вложенные use case
    bulk_create_search_query_daily_stats_use_case = providers.Factory(
        BulkCreateSearchQueryDailyStatsUseCase,
        search_query_daily_stats_repository=search_query_daily_stats_repository,
        get_search_query_by_value_use_case=get_search_query_by_value_use_case,
        bulk_create_search_queries_use_case=bulk_create_search_queries_use_case,
    )

    calculate_total_requests_per_day_use_case = providers.Factory(
        CalculateTotalRequestsPerDayUseCase,
        search_query_total_number_per_day_repository,
    )


class ContainerAlembic(containers.DeclarativeContainer):
    settings = Settings()
    settings.postgres_driver = 'postgresql+psycopg2'

    config = providers.Configuration()
    config.from_dict(settings.model_dump(mode='json'))
