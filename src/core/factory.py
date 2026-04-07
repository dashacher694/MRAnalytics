"""
Simple dependency factory
"""
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.config import settings
from src.db.connection import engine
from src.infrastructure.clients.gitlab import GitLabClient
from src.modules.mr_analytics.application.services import MRAnalyticsService
from src.modules.mr_analytics.infrastructure.persistence.uow import MRPersistenceUnitOfWork
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.get_metrics.impl import GetMetricsUseCase


class Container:
    """Simple dependency container"""
    
    def __init__(self):
        self._db_engine: AsyncEngine = engine
        self._vcs_client: GitLabClient = GitLabClient(
            token=settings.token,
            base_url=settings.base_url,
            project_id=settings.project_id,
            timeout=settings.api_timeout,
        )
        self._analytics_service: MRAnalyticsService = MRAnalyticsService()
    
    @property
    def db_engine(self) -> AsyncEngine:
        return self._db_engine
    
    @property
    def vcs_client(self) -> GitLabClient:
        return self._vcs_client
    
    @property
    def analytics_service(self) -> MRAnalyticsService:
        return self._analytics_service
    
    def persistence_uow(self) -> MRPersistenceUnitOfWork:
        return MRPersistenceUnitOfWork(self._db_engine)
    
    def query_uow(self) -> QueryUnitOfWork:
        return QueryUnitOfWork(self._db_engine)
    
    def process_mrs_usecase(self) -> ProcessMergeRequestsUseCase:
        return ProcessMergeRequestsUseCase(
            uow=self.persistence_uow(),
            analytics_service=self._analytics_service,
        )
    
    def get_metrics_usecase(self) -> GetMetricsUseCase:
        return GetMetricsUseCase(
            uow=self.query_uow(),
        )


# Global container instance
container = Container()
