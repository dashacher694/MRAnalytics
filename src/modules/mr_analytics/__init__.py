"""MR Analytics module"""
from .domain.aggregate.model import MergeRequest, MRMetrics
from .domain.value_objects import Comment, Approval, ReviewRound
from .domain.enums import RiskScore, MRState
from .application.services import MRAnalyticsService
from .infrastructure.persistence.mapper import start_mapper
from .infrastructure import (
    MRMetricsRepository,
    SQLAlchemyMRMetricsRepository,
    AsyncSQLAlchemyUnitOfWork,
    MRMetricsQueryRepository,
    SQLAlchemyMRMetricsQueryRepository,
    QueryUnitOfWork,
    MRMetricsDTO,
    MRAnalyticsSummaryDTO,
    AuthorStatsDTO,
)

__all__ = [
    # Domain models
    "MergeRequest",
    
    # Value objects
    "MRMetrics",
    "Comment",
    "Approval", 
    "ReviewRound",
    
    # Enums
    "RiskScore",
    "MRState",
    
    # Application services
    "MRAnalyticsService",
    
    # Infrastructure
    "MRMetricsRepository",
    "SQLAlchemyMRMetricsRepository",
    "AsyncSQLAlchemyUnitOfWork",
    "MRMetricsQueryRepository", 
    "SQLAlchemyMRMetricsQueryRepository",
    "QueryUnitOfWork",
    "MRMetricsDTO",
    "MRAnalyticsSummaryDTO",
    "AuthorStatsDTO",
    
    # Mapping
    "start_mapper",
]
