from sqlalchemy.ext.asyncio import AsyncSession
from src.persistance.async_repository import AsyncRepository

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics


class MRMetricsRepository(AsyncRepository[MRMetrics, int]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
