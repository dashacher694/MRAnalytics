from sqlalchemy.ext.asyncio import AsyncEngine

from src.modules.mr_analytics.infrastructure.persistence.uow import AsyncSQLAlchemyUnitOfWork
from src.modules.mr_analytics.infrastructure.query.repository.impl import SQLAlchemyMRMetricsQueryRepository
from src.modules.mr_analytics.infrastructure.query.repository.protocol import MRMetricsQueryRepository


class QueryUnitOfWork(AsyncSQLAlchemyUnitOfWork):
    
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def __aenter__(self):
        await super().__aenter__()
        
        self.repository: MRMetricsQueryRepository = SQLAlchemyMRMetricsQueryRepository(self.session)
        return self
