from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics, RiskScore
from src.modules.utils.errors import NotFoundError, BadRequestError
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.application.analytics_services import RiskPredictionService, AnomalyDetectionService
from .command import PredictRiskRequest, PredictRiskResponse


class PredictRiskUseCase(BaseUseCase[QueryUnitOfWork]):
    
    def __init__(self, uow: QueryUnitOfWork) -> None:
        self._uow = uow
    
    @async_transactional(read_only=True)
    async def invoke(self, request: PredictRiskRequest) -> PredictRiskResponse:
        logger.info(f"Predicting risk for MRs in last {days} days")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        metrics = await self.uow.metrics_repository.get_by_date_range(start_date, end_date)
        
        for metric in metrics:
            metric.risk_score = RiskPredictionService.predict_risk(metric)
        
        anomalies = AnomalyDetectionService.find_anomalies(metrics)
        for anomaly in anomalies:
            anomaly.is_anomaly = True
        
        high_risk = sum(1 for m in metrics if m.risk_score == RiskScore.HIGH)
        medium_risk = sum(1 for m in metrics if m.risk_score == RiskScore.MEDIUM)
        low_risk = sum(1 for m in metrics if m.risk_score == RiskScore.LOW)
        anomalies_count = len(anomalies)
        
        risk_dist = {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        }
        
        logger.info(f"Risk prediction completed. High risk: {high_risk}, Anomalies: {anomalies_count}")
        
        return PredictRiskResponse(
            total_analyzed=len(metrics),
            high_risk_count=high_risk,
            medium_risk_count=medium_risk,
            low_risk_count=low_risk,
            anomalies_count=anomalies_count,
            risk_distribution=risk_dist
        )
