from sqlalchemy.orm import registry

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from src.persistance.mr_metrics.entity import MRMetricsEntity

mapper_registry = registry()


def start_mapper():
    mapper_registry.map_imperatively(
        MRMetrics,
        MRMetricsEntity.__table__,
    )
