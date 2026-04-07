from abc import abstractmethod
from typing import List, Protocol
from datetime import datetime

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics


class MRMetricsQueryRepository(Protocol):

    @abstractmethod
    async def get_all(self) -> List[MRMetrics]:
        ...

    @abstractmethod
    async def get_by_iid(self, mr_iid: int) -> MRMetrics | None:
        ...

    @abstractmethod
    async def get_by_author(self, author: str) -> List[MRMetrics]:
        ...

    @abstractmethod
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MRMetrics]:
        ...
